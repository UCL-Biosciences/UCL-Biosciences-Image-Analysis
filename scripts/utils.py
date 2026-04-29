# scripts/utils.py
import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib import cm
from skimage.measure import regionprops, label
from skimage.segmentation import find_boundaries

def plot_mask_overlay(frame, mask, title="Frame with Mask Overlay"):
    """
    Plot original frame with mask overlay.
    """
    plt.figure(figsize=(6, 6))
    plt.imshow(frame, cmap='gray')
    plt.imshow(mask, cmap=cm.nipy_spectral, alpha=0.5)
    plt.title(title)
    plt.axis('off')
    plt.show()

def plot_boundaries(frame, mask, title="Frame with Mask Boundaries"):
    """
    Plot original frame with mask boundaries overlay.
    """
    boundaries = find_boundaries(mask)
    plt.figure(figsize=(6, 6))
    plt.imshow(frame, cmap='gray')
    plt.imshow(boundaries, cmap='autumn', alpha=0.8)
    plt.title(title)
    plt.axis('off')
    plt.show()

def plot_centroids(frame, centroids_df, title="Centroid Positions"):
    """
    Plot frame with centroid positions overlaid.
    
    Args:
        frame (ndarray): Original image frame.
        centroids_df (pd.DataFrame): DataFrame with 'x' and 'y' columns for centroids.
    """
    plt.figure(figsize=(6, 6))
    plt.imshow(frame, cmap='gray')
    plt.scatter(centroids_df['x'], centroids_df['y'], c='r', s=10)
    plt.title(title)
    plt.show()


def plot_size_distribution(masks, file_names, output_dir):
    """
    Generate a histogram of object diameters across all frames and save summary stats.

    Args:
        masks (list): List of segmentation masks for each frame.
        file_names (list): List of image filenames (for reference in summary).
        output_dir (str): Directory to save outputs.
    """
    diameters = []
    frame_labels = []

    for idx, mask in enumerate(masks):
        labelled_mask = label(mask)
        props = regionprops(labelled_mask)
        for prop in props:
            diam = 2 * (prop.area / 3.14159) ** 0.5
            diameters.append(diam)
            frame_labels.append(file_names[idx])

    if not diameters:
        print("No objects found in masks. Skipping size distribution plot.")
        return

    # Create output folder
    validation_dir = os.path.join(output_dir, "validation")
    os.makedirs(validation_dir, exist_ok=True)

    # Plot histogram
    plt.figure(figsize=(8, 5))
    plt.hist(diameters, color='steelblue', edgecolor='black')
    plt.xlabel("Equivalent Diameter (pixels)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Object Diameters")
    plt.tight_layout()
    plt.savefig(os.path.join(validation_dir, "size_distribution.png"), dpi=150)
    plt.close()

    # Compute and save summary stats
    df = pd.DataFrame({
        "frame": frame_labels,
        "diameter_px": diameters
    })
    summary_stats = df["diameter_px"].describe()
    summary_stats.to_csv(os.path.join(validation_dir, "size_distribution_stats.csv"))

    print(f"Size distribution plot saved to: {validation_dir}/size_distribution.png")
    print(f"Summary stats saved to: {validation_dir}/size_distribution_stats.csv")