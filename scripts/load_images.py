# scripts/load_images.py
import tifffile
import glob
import numpy as np
import os
from skimage.transform import resize

def load_images(folder, testing=False, downsize_size=(100, 100)):
    """
    Load a sequence of TIFF files as a 3D numpy array and return file names.
    
    Args:
        folder (str): Directory containing .tif files.
        testing (bool): If True, downsize images to speed up.
        downsize_size (tuple): Size (height, width) for downsizing.
    
    Returns:
        frames (ndarray): Image stack (time, height, width).
        file_names (list): List of original file names.
    """
    tif_files = sorted(glob.glob(os.path.join(folder, "*.tif")))
    if not tif_files:
        raise FileNotFoundError(f"No TIFF files found in folder: {folder}")
    
    print(f"Found {len(tif_files)} TIFF files.")
    
    frames_in = np.stack([tifffile.imread(f) for f in tif_files], axis=0)
    
    if testing:
        print(f"Downsizing frames to {downsize_size} for testing...")
        frames = np.zeros((frames_in.shape[0], downsize_size[0], downsize_size[1]), dtype=frames_in.dtype)
        for i, frame in enumerate(frames_in):
            frames[i] = resize(frame, downsize_size, preserve_range=True).astype(frame.dtype)
    else:
        frames = frames_in
    
    file_names = [os.path.basename(f) for f in tif_files]
    
    return frames, file_names
