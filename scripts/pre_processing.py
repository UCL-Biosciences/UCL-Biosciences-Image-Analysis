import numpy as np
import warnings
from skimage.exposure import rescale_intensity
from skimage.transform import resize


def preprocess_3d_image(img_3d, downsize_factor=None, per_slice=False,
                        apply_gaussian_filter = None, gaussian_sigma = None,
                        sigma_um: tuple[float, float, float] | None = None,
                        voxel_size_um: tuple[float, float, float] | None = None,
                        ram_limit_bytes: int = 2_000_000_000,):
    """
    Preprocess 3D image: 
    normalise + optional resizing (with shape set up by user - could be used for down-sampling)

    Args:
        img_3d: np.ndarray (Z, Y, X)
        downsize_factor: float, factor to downsize the image by (e.g. 0.5 for half size)
        per_slice: bool, if True normalize each slice separately
        apply_gaussian_filter: bool, if True apply gaussian filter
        sigma_um: tuple of float, desired Gaussian sigma in micrometers (Z, Y, X).
        voxel_size_um: tuple of float, physical voxel spacing in micrometers (Z, Y, X). Might be specified in image metadata
        ram_limit_bytes: int, memory warning threshold for gaussian filter

    Returns:
        np.ndarray (Z, Y, X), float32
    """
    img_3d = img_3d.astype('float32')

    if per_slice:
        img_rescaled = np.empty_like(img_3d, dtype='float32')
        for z in range(img_3d.shape[0]):
            img_rescaled[z] = rescale_intensity(img_3d[z], out_range=(0, 1))
    else:
        img_rescaled = rescale_intensity(img_3d, out_range=(0, 1))

    # Check if all slices have the same shape
    shapes = [img.shape for img in img_rescaled]
    if len(set(shapes)) > 1:
        warnings.warn("Images in stack have different sizes.")

    if downsize_factor is not None:
        # Resize the image if downsize_factor is provided
        # first take the first slice to get the shape
        h, w = img_rescaled[0].shape
        #  calculate the output shape based on the downsize factor
        output_shape = [
            int(round(h * downsize_factor, 0)), # height = Y
            int(round(w * downsize_factor, 0)) # width = X
        ]

        # Resize each slice to the output shape
        # Note: resize function expects (Y, X) shape
        # np.stack accepts a list of arrays with the same shape
        img_rescaled = np.stack([
            # resize each slice to the output shape
            resize(img_rescaled[z], output_shape, anti_aliasing=True)
            # by looping through the slices
            for z in range(img_rescaled.shape[0])
        ], axis=0)


    if apply_gaussian_filter:
        # set default sigma if not provided
        if sigma_um is None:
            # warn that gaussian sigma is not provided and will use default
            print("[WARN] gaussian_sigma not provided, using default (1, 1, 1).")
            sigma_um = (1, 1, 1)

        # apply gaussian filter
        img_rescaled = gaussian_filter(img_rescaled,
                                       sigma_um =sigma_um, voxel_size_um=voxel_size_um, ram_limit_bytes=ram_limit_bytes)
    
    return img_rescaled

    ### extra: add alternative methods for pre-processing: gaussian, denoising etc.


def gaussian_filter(
    img: np.ndarray,
    sigma_um: tuple[float, float, float] | None,
    voxel_size_um: tuple[float, float, float] | None,
    ram_limit_bytes: int = 2_000_000_000,
):
    """
    Apply 3D Gaussian filter with guardrails and QC checks.
    Sigma is given in physical units (µm), voxel size must be known.

    Parameters
    ----------
    img : np.ndarray
        3D array with shape (Z, Y, X).
    sigma_um : tuple of float
        Desired Gaussian sigma in micrometers (Z, Y, X).
    voxel_size_um : tuple of float
        Physical voxel spacing in micrometers (Z, Y, X).
        Must not be None.
    ram_limit_bytes : int
        Memory warning threshold.
    """
    from scipy.ndimage import gaussian_filter as gf, sobel
    # ---- pre-checks ----
    assert img.ndim == 3 and np.issubdtype(img.dtype, np.number), "Input must be 3D numeric."
    assert voxel_size_um is not None, "Voxel size must be provided."
    assert len(voxel_size_um) == 3 and all(v > 0 for v in voxel_size_um), "Invalid voxel size."
    assert len(sigma_um) == 3 and all(np.isfinite(s) and s > 0 for s in sigma_um), "Invalid sigma."

    # convert sigma from µm to voxel units
    if sigma_um is None:
        # print warning and set default
        print("[WARN] sigma_um not provided, using default (1, 1, 1) µm.")
        sigma_um = (1.0, 1.0, 1.0)

    # convert sigma from µm to voxel units
    # for each value, divide desired sigma by actual voxel size
    sigma_vox = tuple(s / v for s, v in zip(sigma_um, voxel_size_um))

    # Dynamic range check
    if np.all(img == img.flat[0]):
        print("[WARN] Input is constant intensity.")

    # Memory estimate
    est_bytes = img.size * img.itemsize * 5
    if est_bytes > ram_limit_bytes:
        print(f"[WARN] Estimated RAM {est_bytes/1e9:.2f} GB exceeds limit.")

    # ---- filtering ----
    out = gf(img, sigma=sigma_vox, mode="reflect")

    # ---- post-checks ----
    if out.shape != img.shape:
        print("[FAIL] Shape changed unexpectedly.")

    # mad is a robust noise estimator
    # calculated by median absolute deviation from median
    mad_before = np.median(np.abs(img - np.median(img)))
    mad_after = np.median(np.abs(out - np.median(out)))
    # fractional noise reduction
    # 1e-9 to avoid div by zero
    noise_drop = (mad_before - mad_after) / (mad_before + 1e-9)
    if noise_drop < 0.1:
        print("[WARN] Blur had little effect on noise.")

    # edge preservation check
    # use Sobel filter to estimate edges and make sure they are similar before and after
    # we calculate the mean gradient magnitude across the whole volume
    grad_before = np.mean(np.sqrt(sum(sobel(img, axis=i)**2 for i in range(3))))
    grad_after = np.mean(np.sqrt(sum(sobel(out, axis=i)**2 for i in range(3))))
    # we want the edges to be at least half as strong after blurring
    if grad_after < 0.5 * grad_before:
        print("[WARN] Edges weakened too much (over-smoothing).")

    # print QC, including sigma in voxels, noise drop percentage, and edge ratio
    print(f"Noise↓ {noise_drop*100:.1f}%, Edge ratio (mean gradident before / mean gradient after) {grad_after/grad_before:.2f}")

    return out
