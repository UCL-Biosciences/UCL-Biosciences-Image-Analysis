import tifffile
import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.color import label2rgb
from pathlib import Path  ### switching to pathlib path-handling instead of the os

from skimage.exposure import rescale_intensity
from skimage.util import img_as_ubyte

from cellpose import models
from stardist.models import StarDist3D  ### model loaded from the 
from tifffile import imwrite



### configs ###
cwd = Path.cwd()
project_root = cwd.parent.resolve() # assume "scripts" folder is one level up from cwd
STARDIST_MODEL_DIR = project_root / "models" / "stardist-models"


### functions for segmenting nuclei

def segment_with_cellpose(img_3d, diameter=None, channels=[0,0], gpu=False):
    """
    Segments 3D image using Cellpose.

    Args:
        img_3d: np.ndarray (Z, Y, X)
        model_type: 'nuclei' or 'cyto'
        diameter: estimated object diameter (int), or None to auto-detect
        channels: which channels to use (always [0,0] for grayscale)

    Returns:
        masks: segmentation mask of shape (Z, Y, X)
    """
    print("Running Cellpose...")
    model = models.CellposeModel(gpu=gpu)
    
    masks, flows, styles, diams = model.eval(
    img_3d,
    diameter=diameter,      # diameter can be adjusted fpr better targeted segmentation?
    channels=channels,      # for grayscale (Cellpose expects [0,0] format?)
    z_axis=0,               # specify for Cellpose this is 3D: (Z, Y, X)
    channel_axis=None,      # no channel axis (grayscale)
    do_3D=True              # enables 3D segmentation
    )

    return masks




def segment_with_stardist(img_3d, model_dir=STARDIST_MODEL_DIR, model_name='3d_demo'):
    """
    Segments 3D image using pre-trained StarDist 3D model.

    Returns:
        labels: np.ndarray (Z, Y, X) with instance labels
    """
    print("Running StarDist...")
    #model = StarDist3D.from_pretrained(model_name)
    model = StarDist3D(None, name=model_name, basedir=str(model_dir)) # accessing locally saved model to avoid access restriction issues
    labels, _ = model.predict_instances(    
        img_3d  # image must be normalised
        #axes="ZYX", 
        #prob_thresh=0.5,  # detection probability threshold
        #nms_thresh=0.1,  # remove detections overlapping by more than this threshold
        #scale=1,  # higher values are suitable for lower resolution data
        )
    return labels


### function for segmenting cytoplasm

from skimage.segmentation import watershed
from skimage.filters import gaussian
import numpy as np
from scipy import ndimage as ndi

def segment_cytoplasm(nuclei_mask, cyto_channel, mode="membrane", sigma=1.0,
                      min_signal=0.05, membrane_threshold=0.2):
    """
    Segment cytoplasm using nuclei as seeds and cytoplasmic/membrane channel as guidance.

    Parameters:
    ----------
    nuclei_mask : ndarray
        Labeled nuclei segmentation (3D).
    cyto_channel : ndarray
        Cytoplasmic or membrane channel (3D).
    mode : str
        "membrane" for boundary-based segmentation (membrane marker).
        "cytoskeleton" for intensity-based segmentation (cytoplasmic marker).
    sigma : float
        Gaussian smoothing for the guidance image.
    min_signal : float
        Minimum normalized intensity for cytoplasm mask (for intensity mode).
    membrane_threshold : float
        Threshold for membrane signal to act as stopping boundary.

    Returns:
    -------
    cytoplasm_labels : ndarray
        Labeled cytoplasm mask.
    """
    
    # normalize channel to 0-1
    #channel = preprocess_3d_image(cyto_channel, downsize_factor, per_slice=per_slice_norm)
    
    # smooth channel
    smoothed = gaussian(cyto_channel, sigma=sigma)
    
    if mode == "membrane":
        # binary mask of membrane
        membrane_mask = smoothed > membrane_threshold
        distance = ndi.distance_transform_edt(~membrane_mask)
        cytoplasm_labels = watershed(-distance, markers=nuclei_mask, mask=~membrane_mask)
    
    elif mode == "intensity":
        # cytoplasmic regions to include
        cytoplasm_mask = smoothed > min_signal
        inverted = -smoothed
        cytoplasm_labels = watershed(inverted, markers=nuclei_mask, mask=cytoplasm_mask)
    
    else:
        raise ValueError("Invalid mode. Choose 'membrane' or 'intensity'.")
    
    return cytoplasm_labels