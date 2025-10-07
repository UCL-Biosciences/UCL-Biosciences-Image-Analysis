# 3D Preprocessing
These functions form the preprocessing used in the Jupyter notebook to prepare 3D image stacks for segmentation. They handle intensity normalisation, isotropic resampling, downsampling, and Gaussian filtering. Each function is modular and reusable.

## Main Function: `preprocess_3d_image()`
This is the main entry point for 3D preprocessing. Called from the main workflow (notebook or scripts) to prepare raw input before segmentation. It combines:
- Intensity normalisation (slice-wise or global)
- Optional isotropic resampling (via `resample_to_isotropic()`)
- Optional downsampling in XY (via `downsample_xy()`)
- Optional Gaussian smoothing (via `gaussian_filter()`)

## Isotropy: `resample_to_isotropic()`
Resamples an anisotropic 3D image stack to have uniform voxel spacing across all three dimensions (Z, Y, X). Microscopy images often have different resolution in Z than in Y/X, due to physical or acquisition constraints. For example, Z spacing might be 2 µm while Y/X spacing is 0.5 µm, making objects look stretched or compressed along the Z-axis.

This function ensures that voxels are cubic, which is important for shape analysis, 3D visualisation, and models that assume isotropy. It computes scaling factors relative to the smallest voxel size, and resizes the image accordingly using skimage.transform.resize.

Called inside `preprocess_3d_image()` when `resize_isotropic=True`.

## Downsampling: `downsample_xy()`
Downsamples only the XY dimensions of a 3D image (Z remains unchanged). Reduces memory usage and processing time, especially helpful for:
- Initial testing of segmentation workflows
- Previewing results without full-resolution computation

Accepts a scale factor in (0, 1], which determines the percentage of the original XY resolution to keep (e.g., 0.5 → 50% size). Maintains the number of Z-slices, ensuring compatibility with time-lapse or volumetric sequences. Uses skimage.transform.resize with interpolation. Called by `preprocess_3d_image()` if downsize_factor is specified.

## Gaussian Filter: `gaussian_filter()`
Applies a 3D Gaussian blur using `scipy`'s `gaussian_filter` function. The blur is applied in physical units (µm). The function requires the voxel size (`voxel_size_um`; Z,Y,X) of the image, which is converted to a target sigma (Z,Y,X; specified with `sigma_um`; defaults to (1,1,1)). Runs simple QC checks (noise reduction, edge preservation, memory use) and prints a summary.

The function is called from the main `preprocess_3d_image` function by setting `apply_gaussian_filter` to `True`. `voxel_size_um` is required, others default as below if not entered.

**Arguments**

- `img`: 3D array `(Z, Y, X)`
- `sigma_um`: blur width in µm `(Z, Y, X)`. Defaults to `(1,1,1)`.
- `voxel_size_um`: voxel spacing in µm `(Z, Y, X)`
- `ram_limit_bytes`: int = `2_000_000_000`

Returns the filtered image with same shape.




