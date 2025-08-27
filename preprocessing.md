# 3D Preprocessing
Here we describe the preprocessing steps available and how they are used.

## Gaussian Filter

Applies a 3D Gaussian blur using `scipy`'s `gaussian_filter` function. The blur is applied in physical units (µm). The function requires the voxel size (`voxel_size_um`; Z,Y,X) of the image, which is converted to a target sigma (Z,Y,X; specified with `sigma_um`; defaults to (1,1,1)). Runs simple QC checks (noise reduction, edge preservation, memory use) and prints a summary.

**Arguments**

- `img`: 3D array `(Z, Y, X)`
- `sigma_um`: blur width in µm `(Z, Y, X)`
- `voxel_size_um`: voxel spacing in µm `(Z, Y, X)`

**Returns**
Filtered image with same shape.

**Example**

`blurred = gaussian_filter(img, sigma_um=(2,1,1), voxel_size_um=(2,0.5,0.5))`



