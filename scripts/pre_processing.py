import numpy as np
import warnings
from skimage.exposure import rescale_intensity
from skimage.transform import resize




def preprocess_3d_image(img_3d, downsize_factor=None, per_slice=False):
    """
    Preprocess 3D image: 
    normalize + optional resizing (with shape set up by user - could be used for down-sampling)

    Args:
        img_3d: np.ndarray (Z, Y, X)
        ## output_shape: tuple (Y, X) for resizing; None to keep original
        downsize_factor: float, factor to downsize the image by (e.g. 0.5 for half size)
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

    return img_rescaled

    ### extra: add alternative methods for pre-processing: gaussian, denoising etc.
