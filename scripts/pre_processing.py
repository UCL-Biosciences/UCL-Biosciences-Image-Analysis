import numpy as np
import warnings
from skimage.exposure import rescale_intensity
from skimage.transform import resize


def preprocess_3d_image(img_3d,
                        per_slice=False,
                        resize_isotropic: bool = False,
                        downsize_factor=None,
                        apply_gaussian_filter = None, gaussian_sigma = None,
                        sigma_um: tuple[float, float, float] | None = None,
                        voxel_size_um: tuple[float, float, float] | None = None,
                        ram_limit_bytes: int = 2_000_000_000):
    """
    Preprocess 3D image: 
    normalise + optional resizing (with shape set up by user - could be used for down-sampling)

    Args:
        img_3d: np.ndarray (Z, Y, X)
        per_slice: bool, if True normalize each slice separately
        resize_isotropic: bool, if True resize to isotropic voxel size based on voxel_size_um
        downsize_factor: float, factor to downsize the image by (e.g. 0.5 for half size)
        apply_gaussian_filter: bool, if True apply gaussian filter
        sigma_um: tuple of float, desired Gaussian sigma in micrometers (Z, Y, X).
        voxel_size_um: tuple of float, physical voxel spacing in micrometers (Z, Y, X). Might be specified in image metadata
        ram_limit_bytes: int, memory warning threshold for gaussian filter

    Returns:
        np.ndarray (Z, Y, X), float32
    """
    img_3d = img_3d.astype('float32')

    if per_slice:
        img_3d = np.empty_like(img_3d, dtype='float32')
        for z in range(img_3d.shape[0]):
            img_3d[z] = rescale_intensity(img_3d[z], out_range=(0, 1))
    else:
        img_3d = rescale_intensity(img_3d, out_range=(0, 1))

    # Check if all slices have the same shape
    shapes = [img.shape for img in img_3d]
    if len(set(shapes)) > 1:
        warnings.warn("Images in stack have different sizes.")

    if resize_isotropic: 
        print( "Resizing to isotropic voxel size...")
        if voxel_size_um is None:
            raise ValueError("voxel_size_um must be provided for isotropic resizing.")
        img_3d = resample_to_isotropic(img_3d, voxel_size_um, order=1)

    if downsize_factor is not None:
        print(f"Downsampling XY by factor {downsize_factor}...")
        if not (0 < downsize_factor <= 1):
            raise ValueError("downsize_factor must be in (0, 1].")

        downsample_xy(img_3d, downsize_factor, order=1)

    # if downsize_factor is not None:
    #     # Resize the image if downsize_factor is provided
    #     # first take the first slice to get the shape
    #     h, w = img_rescaled[0].shape
    #     #  calculate the output shape based on the downsize factor
    #     output_shape = [
    #         int(round(h * downsize_factor, 0)), # height = Y
    #         int(round(w * downsize_factor, 0)) # width = X
    #     ]

    #     # Resize each slice to the output shape
    #     # Note: resize function expects (Y, X) shape
    #     # np.stack accepts a list of arrays with the same shape
    #     img_rescaled = np.stack([
    #         # resize each slice to the output shape
    #         resize(img_rescaled[z], output_shape, anti_aliasing=True)
    #         # by looping through the slices
    #         for z in range(img_rescaled.shape[0])
    #     ], axis=0)


    if apply_gaussian_filter:
        print("Applying Gaussian filter...")
        # set default sigma if not provided
        if sigma_um is None:
            # warn that gaussian sigma is not provided and will use default
            print("[WARN] gaussian_sigma not provided, using default (1, 1, 1).")
            sigma_um = (1, 1, 1)

        # apply gaussian filter
        img_3d = gaussian_filter(img_3d,
                                       sigma_um =sigma_um, voxel_size_um=voxel_size_um, ram_limit_bytes=ram_limit_bytes)
    
    return img_3d

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

    # edge preservation check
    # use Sobel filter to estimate edges and make sure they are similar before and after
    # we calculate the mean gradient magnitude across the whole volume
    grad_before = np.mean(np.sqrt(sum(sobel(img, axis=i)**2 for i in range(3))))
    grad_after = np.mean(np.sqrt(sum(sobel(out, axis=i)**2 for i in range(3))))
    # we want the edges to be at least half as strong after blurring
    if grad_after < 0.5 * grad_before:
        print("[WARN] Edges weakened too much (over-smoothing).")

    # print QC, including sigma in voxels, noise drop percentage, and edge ratio
    print(f"MAD before: {mad_before:.4g}, MAD after: {mad_after:.4g}")
    print(f"Edge ratio (mean gradident before / mean gradient after) {grad_after/grad_before:.2f}")

    return out


def resample_to_isotropic(img_3d, voxel_size_um, order=1):
    """
    Resample a 3D image to isotropic voxel spacing by scaling axes relative to the smallest voxel size.

    Parameters
    ----------
    img_3d : np.ndarray
        3D input image with shape (Z, Y, X).
    voxel_size_um : tuple of float
        Physical voxel size (Z, Y, X) in micrometers.
    order : int
        Interpolation order for resizing (1 = bilinear, 3 = bicubic, etc.).

    Returns
    -------
    img_iso : np.ndarray
        Image resampled to isotropic voxel size.
    """
    if img_3d.ndim != 3:
        raise ValueError("Input must be a 3D array (Z, Y, X).")
    
    if len(voxel_size_um) != 3 or any(s <= 0 for s in voxel_size_um):
        raise ValueError("voxel_size_um must be a tuple of 3 positive floats (sz, sy, sx).")

    sz, sy, sx = voxel_size_um
    min_voxel = min(voxel_size_um)
    scale_factors = np.array([sz, sy, sx]) / min_voxel

    new_shape = np.round(np.array(img_3d.shape) * scale_factors).astype(int)

    img_iso = resize(
        img_3d,
        new_shape,
        order=order,
        anti_aliasing=True,
        preserve_range=True
    ).astype(img_3d.dtype)

    return img_iso


def downsample_xy(img_3d, downsize_factor, order=1):
    """
    Downsample the XY dimensions of a 3D image by a given factor.

    Parameters
    ----------
    img_3d : np.ndarray
        3D input image with shape (Z, Y, X).
    downsize_factor : float
        Scaling factor for XY (must be in (0, 1]).
    order : int
        Interpolation order for resizing.

    Returns
    -------
    img_resized : np.ndarray
        XY-downsampled image.
    """
    if not (0 < downsize_factor <= 1):
        raise ValueError("downsize_factor must be in (0, 1].")

    z, y, x = img_3d.shape
    new_y = int(round(y * downsize_factor))
    new_x = int(round(x * downsize_factor))

    img_resized = resize(
        img_3d,
        (z, new_y, new_x),
        order=order,
        anti_aliasing=True,
        preserve_range=True
    ).astype(img_3d.dtype)

    return img_resized
