import os
import matplotlib.pyplot as plt
from matplotlib import cm
from cellpose import models
from skimage.measure import regionprops,label
from skimage.segmentation import find_boundaries
import random
import pandas as pd

def save_mask_overlay(frame, mask, save_path):
    """
    Save overlay of mask on original image.
    
    Args:
        frame (ndarray): Original image.
        mask (ndarray): Segmentation mask.
        save_path (str): File path to save image (e.g., '/output/mask_001.png').
    """
    plt.figure(figsize=(6, 6))
    plt.imshow(frame, cmap='gray')
    plt.imshow(mask, cmap=cm.nipy_spectral, alpha=0.5)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()  # prevent memory leaks

    import os
import matplotlib.pyplot as plt
from skimage.segmentation import find_boundaries

def save_boundary_overlay(frame, mask, save_path):
    """
    Save boundary overlay of mask on original image.
    
    Args:
        frame (ndarray): Original grayscale image.
        mask (ndarray): Segmentation mask.
        save_path (str): File path for saving output.
    """
    boundaries = find_boundaries(mask)
    
    plt.figure(figsize=(6, 6))
    plt.imshow(frame, cmap='gray')
    plt.imshow(boundaries, cmap='autumn', alpha=0.8)  # orange lines
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()


def segment_frames(frames, diameter=None, gpu=False,
                   output_dir=None, save_overlays=False, file_names=None):
    """
    Segment frames using Cellpose model and optionally save overlays.
    
    Args:
        frames (list or ndarray): List or array of frames to segment.
        diameter (float or None): Expected cell diameter (None = auto-estimate).
        gpu (bool): Whether to use GPU.
        output_dir (str): Path to save overlays if save_overlays=True.
        save_overlays (bool): If True, saves mask overlays as PNG.
        file_names (list): Original filenames for labeling outputs.
    
    Returns:
        list: List of masks for each frame.
    """
    model = models.CellposeModel(gpu=gpu)
    masks = []

    if save_overlays and output_dir:
        overlay_dir = os.path.join(output_dir, "masks")
        os.makedirs(overlay_dir, exist_ok=True)

    for i, frame in enumerate(frames):
        print('segmenting image ' + file_names[i])
        mask, *_ = model.eval(frame, diameter=diameter)
        masks.append(mask)

        # Save overlay if requested
        if save_overlays and output_dir:
            print('saving mask for image ' + file_names[i])
            base_name = file_names[i] if file_names else f"frame_{i:03d}.png"
            
            # paths for mask and boundary files
            mask_overlay_path = os.path.join(overlay_dir, f"overlay_{os.path.splitext(base_name)[0]}.png")
            boundary_overlay_path = os.path.join(overlay_dir, f"boundary_{os.path.splitext(base_name)[0]}.png")

            save_mask_overlay(frame, mask, mask_overlay_path)
            save_boundary_overlay(frame, mask, boundary_overlay_path)

    return masks

def estimate_diameter(masks):
    diameters = []
    for mask in masks:
        props = regionprops(mask)
        diameters.extend([2 * np.sqrt(p.area / np.pi) for p in props])
    return np.mean(diameters) if diameters else None


def validate_segmentation_objects(frames, masks, file_names, output_dir,
                                   sample_fraction=0.05, min_samples=5, random_seed=42):
    """
    Validate segmentation by creating labeled QC images and ROI CSV table.

    Args:
        frames (list or ndarray): Frames actually segmented (subset or full set).
        masks (list): Corresponding masks.
        file_names (list): Filenames of these frames.
        output_dir (str): Directory to save outputs.
        sample_fraction (float): Fraction of frames to sample.
        min_samples (int): Minimum number of frames to validate.
        random_seed (int): Seed for reproducibility in sampling.
    """
    qc_dir = os.path.join(output_dir, "validation", "object_labels")
    os.makedirs(qc_dir, exist_ok=True)

    n_frames = len(frames)
    if n_frames <= min_samples:
        sampled_indices = list(range(n_frames))
    else:
        random.seed(random_seed)
        sample_count = max(min_samples, int(n_frames * sample_fraction))
        sampled_indices = random.sample(range(n_frames), sample_count)

    all_props = []
    
    for idx in sampled_indices:
        frame = frames[idx]
        mask = masks[idx]
        fname = file_names[idx]
        
        labelled_mask = label(mask)
        props = regionprops(labelled_mask)
        
        plt.figure(figsize=(6, 6))
        plt.imshow(frame, cmap='gray')
        boundaries = find_boundaries(labelled_mask, mode='outer')  # ensures thin edges
        plt.contour(boundaries, colors='orange', linewidths=0.5)

        for i, prop in enumerate(props, start=1):
            y, x = prop.centroid
            plt.text(x, y, str(i), color='white', fontsize=8, ha='center', va='center')
            
            all_props.append({
                "frame": fname,
                "object_id": i,
                "x": round(x, 2),
                "y": round(y, 2),
                "area_px": prop.area,
                "diameter_px": round(2 * (prop.area / 3.14159) ** 0.5, 2)
            })
        
        save_path = os.path.join(qc_dir, f"qc_{os.path.splitext(fname)[0]}.png")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
    
    df = pd.DataFrame(all_props)
    csv_path = os.path.join(output_dir, "validation", "object_table.csv")
    df.to_csv(csv_path, index=False)

    print(f"QC images saved in: {qc_dir}")
    print(f"ROI table saved at: {csv_path}")
