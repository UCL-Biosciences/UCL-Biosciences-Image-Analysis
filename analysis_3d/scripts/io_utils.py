from pathlib import Path
import glob
import tifffile
import numpy as np
from tifffile import imwrite
from skimage.color import label2rgb
import matplotlib.pyplot as plt


### loading images

def load_multichannel_images(input_folder, channel_map):
    """
    Loads multi-channel 3D images from a folder and returns a structured list 
    with filename and channel-specific volumes.
    
    Args:
        input_folder (str or Path): Folder with .tif files
        channel_map (dict): Mapping like {"nuclei": 0, "cytoplasm": 1, "membrane": 2}

    Returns:
        list of dict: [
            {
                "filename": str,  # original TIFF filename
                "channels": {
                    "nuclei": array(Z,Y,X),
                    "cytoplasm": array(Z,Y,X),
                    ...
                }
            },
            ...
        ]
    """
    input_folder = Path(input_folder)
    files = sorted(input_folder.glob("*.tif")) ### TODO: support handling different formats dynamically, e.g. .tif vs .lif
    
    if not files:
        raise FileNotFoundError("No .tif files found in the folder.")

    all_volumes = []
    for f in files:
        img = tifffile.imread(f)  # could be (Z,Y,X,C) or (C,Z,Y,X)

        if img.ndim != 4:
            raise ValueError(f"Unexpected image shape: {img.shape}. Expected 4D (Z,Y,X,C) or (C,Z,Y,X).")

        # identify channels axis and move it to last
        if img.shape[-1] <= 10:
            zyx_channels = img  # already in (Z,Y,X,C)
        else:
            # guess channel axis (the one with size < 10)
            channel_axis = np.argmin(img.shape)
            if img.shape[channel_axis] < 10:
                zyx_channels = np.moveaxis(img, channel_axis, -1) # moving the channel axis to the last position
            else:
                raise ValueError(f"Cannot determine channel axis for shape {img.shape}")

        # map channels to names
        channels_dict = {}
        for name, idx in channel_map.items():
            if idx >= zyx_channels.shape[-1]:
                raise IndexError(f"Channel index {idx} for '{name}' out of range in image {f.name}")
            channels_dict[name] = zyx_channels[..., idx]

        # append structured entry with filename and channels (per image)
        all_volumes.append({
            "filename": f.stem, 
            "channels": channels_dict
        })

    return all_volumes



### saving segmentation outputs

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
    Save segmentation masks and optional overlays in a flat structure.

    Parameters
    ----------
    volume : np.ndarray
        Original image stack (Z,Y,X) or (Z,Y,X,C)
    mask : np.ndarray
        Segmentation mask (Z,Y,X)
    output_root : Path or str
        Root folder to save results
    experiment_label : str or Path
        Can be full path to original file, or just a string label.
        The stem (filename without extension) will be used as the folder name.
    save_overlay : bool
        Whether to save maximum intensity projection overlay
    """
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True) # create output directory

    # save mask stack with experiment label in filename
    mask_uint16 = mask.astype(np.uint16)
    mask_path = output_root / f"{experiment_label}_mask.tif"
    imwrite(mask_path, mask_uint16)
    print(f"[INFO] Saved mask stack: {mask_path}")
    
    # save MIP overlay if requested
    if save_overlay:
        # compute MIP of raw volume
        if volume.ndim == 4:  # if multichannel, assume first channel for MIP
            mip_raw = np.max(volume[..., 0], axis=0)
        else:
            mip_raw = np.max(volume, axis=0)

        mip_mask = np.max(mask, axis=0)

        # normalize raw MIP for display
        mip_raw_float = mip_raw.astype(np.float32)
        mip_raw_float = (mip_raw_float - mip_raw_float.min()) / (
            mip_raw_float.max() - mip_raw_float.min() + 1e-8
        )

        # overlay labels on raw MIP
        mip_overlay = label2rgb(mip_mask, image=mip_raw_float, bg_label=0, alpha=0.4)

        overlay_path = output_root / f"{experiment_label}_overlay_MIP.png"
        plt.imsave(overlay_path, (mip_overlay * 255).astype(np.uint8))
        plt.close()
        print(f"[INFO] Saved MIP overlay: {overlay_path}")

