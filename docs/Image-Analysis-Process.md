# Image Analysis Process
The image analysis workflow can be tricky to follow. There are multiple steps and each can have many options. Plus, you only know whether you chose the right option much later, before having to go back to an earlier step to try a different approach. If you don't approach it in an organised way, it can be confusing. So we thought we would lay out some general steps for processing image data to identify, segment and quantify images.

## Segmentation Decisions
Segmentation of bioimages is a decision process, not a single algorithm. Classic (non-deep-learning) methods work well for many fluorescence datasets, but performance depends on contrast, object size, touching rate, and staining consistency. This guide provides a structured workflow and routing logic so users do not jump randomly between filters and thresholds.

Here, we just describe the steps briefly. For more info, see e.g. [this guide](https://haesleinhuepf.github.io/BioImageAnalysisNotebooks/20_image_segmentation/readme.html).

The framework follows a simple sequence:

1. Record key information about your images
2. Preprocessing. Clean the image by reducing noise, adjusting contrast, and correcting background.
3. Foreground masks. Identify and isolate regions of interest with binary segmentation.
4. Generate seeds. Mark initial points inside objects to guide segmentation.
5. Separate objects with watershed. Use boundary information to split touching or overlapping objects into separate regions.
6. Refine masks. Post-process masks with morphological operations (e.g., erosion, dilation, hole filling) to clean boundaries.
7. Quality-check. Compare automated outputs against expexted or ground truth annotations to assess accuracy.

Each stage has clear decision points. If the required conditions are not met, the user branches appropriately (e.g. improve contrast or adjust seeding rather than forcing a failing threshold). The aim is to reduce guesswork and keep workflows simple and reproducible.

## 1. Record Key Info
As with all data analysis, understanding your data is crucial for efficient and robust analysis. These are some of the important things to think about as you start image analysis.

Object: nuclei / whole cells / sub-objects

Imaging: fluorescence / brightfield; channels used for object vs boundary

Size range: expected pixel area or diameter. Calculate:

- effective_px_size = camera_px_size / magnification
- effective_px_size_after_binning = effective_px_size × bin_factor
- expected_pixel_diameter = physical_diameter / effective_px_size_after_binning

Touching frequency: low / medium / high

Shape: round / elongated / irregular

Signal reliability: consistent / variable (across field, across batch)

Error tolerance: more acceptable to miss objects or to over-split?

## Why this matters ##
Size → filters and distance-transform parameters

Touching → need for seeds and watershed

Shape → distance peaks vs erosion vs skeleton seeds

Signal quality → global vs adaptive thresholding

Error preference → threshold and watershed aggressiveness

# If missing information
If you cannot estimate size and touching rate, inspect ~50 fields and measure.

If you do not know whether contrast is stable, check across plates/batches.

## 2. Preprocessing
Preprocessing is the initial stage of bioimage analysis where raw microscopy images are cleaned and standardised before further processing. The goal is to improve image quality, reduce artifacts, and make biological structures easier to detect and quantify. Without preprocessing, downstream steps like segmentation or feature extraction may be inaccurate or unreliable.

Key steps include:

- Background correction: Remove uneven illumination or shading to highlight true signal.
- Denoising: Reduce random noise while preserving fine details of cells or structures.
- Normalisation: Scale intensity values to a consistent range for comparability across samples.
- Contrast enhancement: Improve visibility of faint structures by adjusting intensity levels.

## 3. Foreground Masks
Foreground mask extraction is the process of separating meaningful biological structures (cells, tissues, organelles) from the background in an image. This step isolates regions of interest so that downstream analysis (segmentation, counting, intensity measurement) focuses only on biologically relevant pixels rather than noise or background. It produces a "mask", which means each pixel has one of two values - true (foreground) or false (background).

Key steps include:
- Thresholding: Apply intensity cutoffs (global or adaptive) to distinguish signal from background.
- Binary conversion: Transform the image into a mask where foreground pixels are marked as 1 and background as 0.
- Morphological cleanup: Refine masks by removing small specks, filling holes, or smoothing edges.
- Region selection: Keep only connected components that match expected object size or shape.

## 4. Generate seeds
Seed generation is the process of placing initial marker points inside objects of interest to guide segmentation algorithms. Seeds act as starting references that help distinguish individual objects, especially when they are touching or overlapping, ensuring more accurate separation.

Key steps include:
- Local maxima detection: Identify bright intensity peaks within objects as seed points.
- Distance transform: Compute distance from background to find object centers for seed placement.
- Marker assignment: Label each seed uniquely to represent different objects.
- Validation: Ensure seeds are correctly positioned inside objects and not in background regions.

## 5. Separate objects with watershed
Watershed segmentation is a technique that treats the image like a topographic surface, where intensity values represent elevation, and “flooding” separates regions into distinct basins. It is especially useful for splitting touching or overlapping objects (e.g., clustered cells) into individual segments, ensuring accurate object boundaries.

Key steps include:
- Gradient computation: Highlight edges and boundaries to define the “terrain.”
- Marker placement: Use seeds or predefined markers to indicate starting points for flooding.
- Flooding process: Expand regions outward until they meet, forming clear object boundaries.
- Post-processing: Refine results by merging small fragments or correcting over-segmentation.

Separating objects is a critical step that can produce:
- Object boundaries: Clear outlines of cells, nuclei, or other structures.
- Binary masks: Pixel‑level maps separating foreground (objects) from background.
- Labeled regions: Each object assigned a unique identifier for counting and tracking.

## 6. Refine masks
Improving raw segmentation masks to better match biological structures. Raw masks often contain noise, holes, or fragmented regions that can distort measurements.

Key steps include:
- Apply morphological operations (e.g., erosion, dilation, hole filling).
- Remove small specks or merge fragmented regions.
- Filter objects by expected size or shape ranges.

## 7. Quality-check
Assessing whether segmentation results are accurate and biologically meaningful. Ensures that downstream analysis (counts, intensity, tracking) is based on reliable data.

Key steps include:
- Compare masks against ground truth or expert annotations.
- Check consistency with biological expectations (e.g., realistic cell counts, fluorescence levels).
- Flag and correct over‑segmentation or under‑segmentation errors.