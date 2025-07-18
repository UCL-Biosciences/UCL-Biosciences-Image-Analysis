# scripts/measure.py
from skimage.measure import regionprops
import numpy as np

def estimate_diameter(masks):
    """
    Estimate mean cell diameter based on segmentation masks.
    
    Args:
        masks (list): List of 2D numpy arrays representing cell masks.
    
    Returns:
        float: Estimated mean diameter of detected cells (in pixels).
    """
    diameters = []
    for mask in masks:
        props = regionprops(mask)
        diameters.extend([2 * np.sqrt(p.area / np.pi) for p in props])
    
    return np.mean(diameters) if diameters else None
