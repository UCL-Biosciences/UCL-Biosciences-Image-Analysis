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




def segment_with_stardist(img_3d, model_dir=STARDIST_MODEL_DIR, model_name='3D_demo'):
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




### segmentation utils

def overlay_segmentation(img, mask, z_slice=None):
    z = z_slice if z_slice is not None else img.shape[0] // 2  ## uses middle slice by default
    overlay = label2rgb(mask[z], image=img[z], bg_label=0, alpha=0.4, bg_color=None)
    
    plt.figure(figsize=(6, 6))
    plt.imshow(overlay)
    plt.title(f"Overlay (Z={z})")
    plt.axis('off')
    plt.show()


def save_mask_as_tiff(mask, output_path):
    """
    Save 3D mask as a TIFF stack.
    """
    tifffile.imwrite(output_path, mask.astype(np.uint16))
    print(f"Saved segmentation mask to {output_path}")


def save_segmentation_results(volume, mask, output_root, experiment_label, save_overlay=True):
    """
    Save segmentation masks and optional overlays.
    
    Parameters
    ----------
    volume : np.ndarray
        Original image stack (Z, Y, X) or (Z, Y, X, C)
    mask : np.ndarray
        Segmentation mask (Z, Y, X)
    output_root : Path or str
        Folder to save results
    experiment_label : Path or str
        Can be full path to original file, or just a string label.
        The stem (filename without extension) will be used as the folder name.
    save_overlay : bool
        Whether to save maximum intensity projection overlay
    """
    output_root = Path(output_root)
    experiment_label = Path(experiment_label).stem  # ensures only filename part is used
    
    # Create experiment directory
    experiment_dir = output_root / experiment_label
    experiment_dir.mkdir(parents=True, exist_ok=True)

    # Save full mask stack as uint16
    mask_uint16 = mask.astype(np.uint16)
    mask_path = experiment_dir / "mask.tif"
    imwrite(mask_path, mask_uint16)
    print(f"Saved mask stack to {mask_path}")

    if save_overlay:
        # Handle multi-channel case
        if volume.ndim == 4:
            mip_raw = np.max(volume[..., 0], axis=0)  # assume channel 0 is raw/nuclei
        else:
            mip_raw = np.max(volume, axis=0)  # (Y, X)

        mip_mask = np.max(mask, axis=0)   # (Y, X)

        # Normalize raw MIP to 0–1
        mip_raw_float = mip_raw.astype(np.float32)
        mip_raw_float = (mip_raw_float - mip_raw_float.min()) / (
            mip_raw_float.max() - mip_raw_float.min() + 1e-8
        )

        # Create RGB overlay
        mip_overlay = label2rgb(
            mip_mask, image=mip_raw_float, bg_label=0, alpha=0.4, bg_color=None
        )

        # Save overlay
        overlay_path = experiment_dir / "overlay_MIP.png"
        plt.imwrite(overlay_path, (mip_overlay * 255).astype(np.uint8))
        plt.close()
        print(f"Saved MIP overlay to {overlay_path}")