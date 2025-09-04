##### quantification #####
import numpy as np
import pandas as pd


# 1. count, volume and intensity options

def quantify_objects(mask: np.ndarray,
                     intensity_img: np.ndarray = None,
                     voxel_size=(1, 1, 1),
                     features=("count", "volume", "intensity")):
    """
    Quantify objects in a 3D segmentation mask.

    Parameters
    ----------
    mask : np.ndarray (Z, Y, X)
        Labeled or binary mask (0 = background, 1..N = objects).
    intensity_img : np.ndarray (Z, Y, X), optional
        Image to measure intensities from (e.g., organelle channel).
    voxel_size : tuple of float
        Physical voxel dimensions  (Z, Y, X). Used for volume calculation.
    features : tuple of str
        Which features to compute. Options:
        - "count"     : number of objects
        - "volume"    : object volumes (and mean volume)
        - "intensity" : per-object mean intensity (requires intensity_img)

    Returns
    -------
    df : pd.DataFrame
        Table of per-object properties (depends on selected features).
    summary : dict
        Global summary metrics (depends on selected features).
    """
    from skimage.measure import regionprops_table, label

    # label if mask is only binary
    if mask.dtype == bool or np.array_equal(np.unique(mask), [0, 1]):
        mask = label(mask)

    # --- selecting which features to extract ---
    # always computing label + centroid
    props = ["label", "centroid"]
    # optional features
    if "volume" in features:
        props.append("area")    ### prop.area in 3d is the voxel-based volume of the object
    if "intensity" in features and intensity_img is not None:
        props.append("mean_intensity")  # mean intensity per object

    # --- extracting selected features (skimage.measure-based) ---
    props_table = regionprops_table(
        mask,
        intensity_image=intensity_img if "intensity" in features else None,
        properties=props
    )
    df = pd.DataFrame(props_table)

    # convert voxel area to real volume
    if "volume" in features and "area" in df:
        voxel_vol = np.prod(voxel_size) if voxel_size is not None else 1
        df["volume"] = df["area"] * voxel_vol
        df.drop(columns=["area"], inplace=True)

    # summary
    summary = {}
    if "count" in features:
        summary["object_count"] = len(df)
    if "volume" in features and "volume" in df:
        summary["mean_volume"] = df["volume"].mean() if len(df) > 0 else 0
    if "intensity" in features and "mean_intensity" in df:
        summary["mean_intensity"] = df["mean_intensity"].mean() # mean intensity per image (of per-object mean intensities)

    return df, summary


def quantify_structures_per_cell(
    object_mask,
    cytoplasm_mask,
    intensity_img=None,
    voxel_size=(1,1,1),
    features=("count", "volume", "intensity"),
    return_level="cell"  # options: "cell", "object", "both"
):
    """
    Quantify objects (e.g., spots/organelles) per cell from a segmentation.

    Parameters
    ----------
    object_mask : np.ndarray (Z, Y, X)
        Labeled segmentation mask of objects (0 = background, 1..N = objects).
    cytoplasm_mask : np.ndarray (Z, Y, X)
        Labeled mask of cells (0 = background, 1..M = cells).
    intensity_img : np.ndarray (Z, Y, X), optional
        Image to measure intensities from (e.g., organelle channel).
    voxel_size : tuple of float
        Physical voxel dimensions (z, y, x). Used for volume calculation.
    features : tuple of str
        Which features to compute. Options:
        - "count"     : number of objects per cell
        - "volume"    : per-object volume and per-cell total volume
        - "intensity" : per-object mean intensity + per-cell mean intensity
    return_level : {"cell", "object", "both"}
        Whether to return results at the object level, cell level, or both.

    Returns
    -------
    results : pd.DataFrame or (df_obj, df_cell)
        If "object": per-object table
        If "cell"  : per-cell aggregated table
        If "both"  : tuple of (df_obj, df_cell)
    """
    from skimage.measure import regionprops_table, label

    # preparing strucutre mask
    if object_mask.dtype == bool or np.unique(object_mask).tolist() == [0,1]:
        object_mask = label(object_mask).astype(np.int32)  # # if mask is binary/boolean, label it and cast to integer
    else:
        object_mask = object_mask.astype(np.int32)          # float to integer


    # --- 1) object-level quantification ---
    props = ['label', 'centroid']
    if "volume" in features:
        props.append("area")
    if "intensity" in features and intensity_img is not None:
        props.append("mean_intensity")

    props_table = regionprops_table(
        object_mask,
        intensity_image=intensity_img if "intensity" in features else None,
        properties=props
    )
    df_obj = pd.DataFrame(props_table)

    # convert voxel counts into real volumes
    if "volume" in features and "area" in df_obj:
        voxel_vol = np.prod(voxel_size) if voxel_size is not None else 1
        df_obj["volume"] = df_obj["area"] * voxel_vol
        df_obj.drop(columns=["area"], inplace=True)

    # --- 2) cell-level measurements (cell volumes) ---
    cell_props = regionprops_table(
        cytoplasm_mask,
        properties=["label", "area"]
    )
    df_cell = pd.DataFrame(cell_props)
    if "volume" in features and "area" in df_cell:
        voxel_vol = np.prod(voxel_size) if voxel_size is not None else 1
        df_cell["cell_volume"] = df_cell["area"] * voxel_vol        # getting real-size volume, based on the voxel size, if known
        df_cell.drop(columns=["area"], inplace=True)

    # --- 3) map each object to its parent cell ---
    #n_cells = cytoplasm_mask.max()      # getting the highest number of the mask labels to get the number of cells
    obj_cell_ids = []
    for z, y, x in zip(df_obj["centroid-0"], df_obj["centroid-1"], df_obj["centroid-2"]):   # taking centroid coordinates for each object (e.g. spot)
        cz, cy, cx = int(round(z)), int(round(y)), int(round(x))                            # round them to integers
        cell_id = cytoplasm_mask[cz, cy, cx]                                                # searching for a mask with the same coordinates and assign a corresponding cell_id to the object
        obj_cell_ids.append(cell_id)                                                        # add cell_id column to df_obj, linking every object to a specific cell
    df_obj["cell_id"] = obj_cell_ids

    # --- 4) aggregate features per cell ---
    # start with all cell_ids to preserve empty ones
    df_cell = df_cell.rename(columns={"label": "cell_id"})
    if "count" in features:
        counts = df_obj.groupby("cell_id").size()
        df_cell["object_count"] = df_cell["cell_id"].map(counts).fillna(0).astype(int)      # map total number of objects per cell, assign 0 to cells without objects
    
    if "volume" in features and "volume" in df_obj:
        volumes = df_obj.groupby("cell_id")["volume"].sum()
        df_cell["total_object_volume"] = df_cell["cell_id"].map(volumes).fillna(0)          # get total volume of objects per cell, assign 0 to cells without objects

        # normalise total object volume by cell volume
        if "cell_volume" in df_cell:
            df_cell["object_volume_fraction"] = (
                df_cell["total_object_volume"] / df_cell["cell_volume"]     
            ).fillna(0)
        
        # calulate mean object volume, normalised by cell volume
        if "cell_volume" in df_cell:
            mean_volumes = df_obj.groupby("cell_id")["volume"].mean()
            df_cell["mean_volume_per_cell_volume"] = (
                df_cell["cell_id"].map(mean_volumes) / df_cell["cell_volume"]
            ).fillna(0)

    if "intensity" in features and "mean_intensity" in df_obj:
        mean_intensities = df_obj.groupby("cell_id")["mean_intensity"].mean()
        df_cell["mean_object_intensity"] = df_cell["cell_id"].map(mean_intensities).fillna(0)

    # --- 5) return as requested ---
    if return_level == "object":
        return df_obj
    elif return_level == "cell":
        return df_cell
    elif return_level == "both":
        return df_obj, df_cell
    else:
        raise ValueError("return_level must be one of {'cell','object','both'}")


# 2. compute centroids (either between objects of the same mask or between different channels)
def compute_centroid_distances(mask1, mask2=None, mode="nearest", k=3, voxel_size=(1,1,1)):
    """
    Compute distances between centroids of objects in 3D masks.

    Parameters
    ----------
    mask1 : np.ndarray
        Labeled segmentation mask (ZYX). Each object must have a unique integer ID > 0.
    mask2 : np.ndarray or None, optional
        Second mask for cross-comparison. If None, compares objects within mask1.
    mode : str, optional
        Type of output to return:
            - "matrix"  : full pairwise distance matrix (most heavy, not recommended unless required for downstream analysis)
            - "nearest" : nearest-neighbor distance for each object
            - "kNN"     : distances to k nearest neighbors (default k=3)
            - "summary" : summary statistics (mean, median, std, min, max per object) for the nearest-neighbor distances
    k : int, optional
        Number of nearest neighbors (only used if mode="kNN").
    spacing : tuple of float, optional
        Physical voxel size (z,y,x) to scale coordinates into physical units.

    Returns
    -------
    dict
        Dictionary containing centroids and requested distance measures.
    """
    from skimage.measure import regionprops_table, label
    from scipy.spatial.distance import cdist

    # --- extract centroids ---
    props1 = regionprops_table(mask1, properties=("label", "centroid"))
    centroids1 = np.array([props1[f"centroid-{ax}"] for ax in range(3)]).T * voxel_size

    if mask2 is None:
        centroids2, labels2 = centroids1, props1["label"]
    else:
        props2 = regionprops_table(mask2, properties=("label", "centroid"))
        centroids2 = np.array([props2[f"centroid-{ax}"] for ax in range(3)]).T * voxel_size
        labels2 = props2["label"]

    # --- compute distance matrix ---
    dist_matrix = cdist(centroids1, centroids2)

    result = {"centroids1": centroids1, "labels1": props1["label"]}

    if mask2 is not None:
        result["centroids2"] = centroids2
        result["labels2"] = labels2

    # --- select mode ---
    if mode == "matrix":
        result["dist_matrix"] = dist_matrix

    elif mode == "nearest":
        nearest = dist_matrix.min(axis=1)
        result["nearest"] = nearest

    elif mode == "kNN":
        k = min(k, dist_matrix.shape[1])
        knn = np.sort(dist_matrix, axis=1)[:, :k]
        result["kNN"] = knn

    elif mode == "summary":
        nearest = dist_matrix.min(axis=1)
        result["summary"] = {
            "mean": np.mean(nearest),
            "median": np.median(nearest),
            "std": np.std(nearest),
            "min": np.min(nearest),
            "max": np.max(nearest),
        }

    else:
        raise ValueError(f"Unknown mode: {mode}")

    return result


#### extra:

def tidy_mask(mask_zyx, min_voxels=50, hole_area_max=64, closing_radius=1):
    """
    Creating a cleaner version of masks by removing small objects
    """
    from skimage.morphology import remove_small_holes, remove_small_objects
    from skimage.morphology import ball, binary_closing
    from skimage.measure import label

    # ensure binary for morphology
    binary = mask_zyx > 0
    if closing_radius > 0:
        selem = ball(closing_radius)
        binary = binary_closing(binary, selem)
    binary = remove_small_holes(binary, area_threshold=hole_area_max)
    binary = remove_small_objects(binary, min_size=min_voxels)
    # relabel to instances
    return label(binary)

def filter_mask_by_size(mask: np.ndarray,
                        expected_d_um: float,
                        tol: float = 0.25,
                        voxel_size=(1.0,1.0,1.0),
                        return_df: bool = False):
    """
    Filter labeled mask objects based on expected size (µm³).
    
    Parameters
    ----------
    mask : np.ndarray
        Labeled mask (Z,Y,X).
    expected_d_um : float
        Expected object diameter in µm.
    tol : float
        Fractional tolerance around expected diameter (default ±25%).
    voxel_size : tuple
        Voxel dimensions in µm for volume conversion.
    return_df : bool
        If True, also return DataFrame with kept/removed object stats.
    
    Returns
    -------
    filtered_mask : np.ndarray
        Mask where only objects within size tolerance remain.
    df (optional) : pd.DataFrame
        Object table with columns: label, volume_vox, volume_um3, keep.
    """
    from skimage.measure import regionprops, label

    voxel_vol = np.prod(voxel_size)

    # expected volume range in um3
    min_um3 = sphere_volume_um3(expected_d_um * (1 - tol))
    max_um3 = sphere_volume_um3(expected_d_um * (1 + tol))
    
    props = regionprops(mask)
    keep_labels = []
    rows = []

    for p in props:
        vol_vox = p.area
        vol_um3 = vol_vox * voxel_vol
        keep = (vol_um3 >= min_um3) and (vol_um3 <= max_um3)
        if keep:
            keep_labels.append(p.label)
        rows.append({
            "label": p.label,
            "volume_vox": vol_vox,
            "volume_um3": vol_um3,
            "keep": keep
        })
    
    # build filtered mask (keep labels that passed the threshold)
    filtered_mask = np.where(np.isin(mask, keep_labels), mask, 0)

    if return_df:
        return filtered_mask, pd.DataFrame(rows)
    else:
        return filtered_mask

def build_object_to_cell_map(struct_labeled, df_obj):
    """
    Map each labeled structure object to its parent cell id (from df_obj['cell_id']) (output of quantify_structures_per_cell in scripts.quantification).
    Returns an int32 volume where voxels of object k are set to its cell_id.
    """
    mapped = np.zeros_like(struct_labeled, dtype=np.int32)

    # fast vectorized fill: only operate where there are objects
    mask = struct_labeled > 0
    obj_ids = struct_labeled[mask].astype(int)

    # dict: object_label -> cell_id
    lbl2cell = dict(zip(df_obj["label"].astype(int), df_obj["cell_id"].astype(int)))

    # vectorized lookup (unseen labels -> 0)
    get_cell = np.vectorize(lambda l: lbl2cell.get(l, 0))
    mapped[mask] = get_cell(obj_ids)
    return mapped

def save_struct_mip_overlay_by_cell(struct_labeled, df_obj, raw_volume, out_png):
    """
    Save a MIP overlay where structures are colored by their parent cell id.
    raw_volume: (Z,Y,X) original/preprocessed intensity (used as background)
    """
    from skimage.color import label2rgb
    import matplotlib.pyplot as plt

    mapped = build_object_to_cell_map(struct_labeled, df_obj)

    # sanity checks
    print("Unique cell ids in df_obj:", np.unique(df_obj["cell_id"]))
    print("Unique values in mapped mask:", np.unique(mapped))

    # MIPs
    mip_raw = raw_volume.max(axis=0).astype(np.float32)
    # normalize for display
    mip_raw = (mip_raw - mip_raw.min()) / (mip_raw.max() - mip_raw.min() + 1e-8)

    mip_map = mapped.max(axis=0)

    # label2rgb will color by integer value (cell id)
    overlay = label2rgb(mip_map, image=mip_raw, bg_label=0, alpha=0.4)
    plt.imsave(out_png, (overlay * 255).astype(np.uint8))
    print(f"[INFO] Saved structure→cell overlay MIP to {out_png}")


##### calculations #####

def sphere_volume_um3(d_um):
    """
    Derive threshold from expected diameters (if expected nucelar diameter is known, in um)

    """
    r = d_um / 2.0
    return (4.0/3.0) * np.pi * (r**3)


def get_voxel_size(path):
    """
    Extract voxel size from an OME-TIFF file (path).
    Returns (Z, Y, X) in micrometers if available, otherwise None.
    """
    import tifffile
    from ome_types import from_xml

    with tifffile.TiffFile(path) as tif:
        if tif.ome_metadata:  # OME-XML present
            omexml = from_xml(tif.ome_metadata)
            pixels = omexml.images[0].pixels
            return (
                pixels.physical_size_z,
                pixels.physical_size_y,
                pixels.physical_size_x,
            )
        else:
            return None  # fallback → ask user to input manually






