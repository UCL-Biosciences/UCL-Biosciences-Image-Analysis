import numpy as np
from skimage.exposure import rescale_intensity
from skimage.transform import resize




def preprocess_3d_image(img_3d, output_shape=None, per_slice=False):
    """
    Preprocess 3D image: 
    normalize + optional resizing (with shape set up by user - could be used for down-sampling)

    Args:
        img_3d: np.ndarray (Z, Y, X)
        output_shape: tuple (Y, X) for resizing; None to keep original
        per_slice: bool, if True normalize each slice separately

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

    if output_shape is not None:
        img_rescaled = np.stack([
            resize(img_rescaled[z], output_shape, anti_aliasing=True)
            for z in range(img_rescaled.shape[0])
        ], axis=0)

    return img_rescaled

    ### extra: add alternative methods for pre-processing: gaussian, denoising etc.
