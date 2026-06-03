# Image Analysis Process

This document outlines a general workflow for segmenting and quantifying objects in microscopy images. It is not exhaustive, it as a starting framework, not a fixed recipe. Each step requires you to inspect the output and decide whether it is good enough before moving on.

For broader introductions to bioimage analysis, see [this guide](https://haesleinhuepf.github.io/BioImageAnalysisNotebooks/20_image_segmentation/readme.html).

---

## Workflow Overview

1. Record key information about your images
2. Preprocess — reduce noise, correct background, normalise intensity
3. Create a foreground mask — separate signal from background
4. Generate seeds — mark object centres to guide separation
5. Run watershed — split touching or overlapping objects
6. Refine masks — clean up boundaries and filter by size/shape
7. Quality-check — verify results against expectations or ground truth

---

## Step 1: Record Key Information

Before writing a single line of analysis, understand your data. The decisions you make in every subsequent step depend on what you record here.

| Property | What to note |
|---|---|
| **Object type** | Nuclei, whole cells, organelles, other |
| **Imaging modality** | Fluorescence or brightfield; which channel marks the object vs boundary |
| **Expected size** | Approximate diameter or pixel area |
| **Confluency** | How often objects touch — low, medium, or high |
| **Shape** | Round, elongated, or irregular |
| **Signal consistency** | Does intensity vary across fields, wells, or batches? |
| **Error tolerance** | Is it worse to miss objects, or to over-split them? |

**Why this matters:**

- **Size** determines filter scales and distance-transform parameters.
- **Confluency** tells you whether you need seeds and watershed at all.
- **Shape** guides your choice of seeding strategy (intensity peaks vs erosion vs skeletonisation).
- **Signal consistency** determines whether global or adaptive thresholding is appropriate.
- **Error tolerance** sets how aggressive your thresholds and watershed should be.

> If you cannot estimate size or touching frequency, inspect ~50 fields and measure before proceeding. If you are unsure whether contrast is stable, check across plates or batches first.

---

## Step 2: Preprocessing

Raw microscopy images nearly always need cleaning before analysis. Skipping this step leads to unreliable segmentation downstream.

- **Background correction:** Remove uneven illumination or shading artefacts so that signal reflects biology, not optics.
- **Denoising:** Reduce random noise while preserving structural detail.
- **Intensity normalisation:** Scale values to a consistent range so images are comparable across samples or timepoints.
- **Contrast enhancement:** Improve visibility of faint structures by adjusting intensity levels.

Inspect the output before moving on. Ask: does the signal look clean and even? Are structures clearly visible?

---

## Step 3: Foreground Mask

A foreground mask is a binary image — each pixel is either object (1) or background (0). The goal is to isolate the pixels that contain biologically meaningful signal.

- **Thresholding:** Apply an intensity cutoff (global or adaptive) to separate signal from background.
- **Binary conversion:** Convert the thresholded image to a mask.
- **Morphological cleanup:** Remove small noise specks, fill holes, smooth edges.
- **Region filtering:** Discard connected components that are too small or too large to be real objects.

The mask does not need to separate individual objects yet — that comes later. It just needs to correctly capture which pixels are foreground.

---

## Step 4: Generate Seeds

Seeds are marker points placed inside individual objects to guide the watershed step. They are especially important when objects are touching or overlapping.

- **Local maxima detection:** Find intensity peaks within objects.
- **Distance transform:** Compute the distance from the background to identify object centres — useful when intensity peaks are unreliable.
- **Marker assignment:** Give each seed a unique label.
- **Validation:** Check that seeds sit inside objects, not in background or on borders.

One seed per object is the goal. Too few seeds and objects merge; too many and objects over-split.

---

## Step 5: Watershed Segmentation

Watershed treats the image as a topographic surface and "floods" it from the seed points outward, stopping where regions meet. It is the standard approach for separating touching objects.

- **Gradient computation:** Generate an edge map to define object boundaries.
- **Flooding from seeds:** Expand each labelled region until it meets a neighbouring region.
- **Post-processing:** Merge small fragments or correct obvious over-segmentation.

Output is a labelled image where each object has a unique integer ID — ready for measurement.

---

## Step 6: Refine Masks

Raw watershed output often has rough boundaries or small artefacts. Refinement brings the masks closer to the true object outlines.

- Apply morphological operations: erosion, dilation, hole filling as needed.
- Remove objects below or above expected size thresholds.
- Filter by shape descriptors (e.g., circularity, aspect ratio) if your objects have a consistent form.

---

## Step 7: Quality Check

Do not skip this step. Errors in segmentation propagate directly into your quantitative results.

- Overlay masks on the raw image and visually inspect a representative sample of fields.
- Compare object counts and sizes against biological expectations.
- If ground truth annotations are available, compute standard metrics (precision, recall, F1, Jaccard index).
- Identify systematic errors: consistent over-segmentation, missed objects in dim regions, boundary artefacts.

If quality is insufficient, return to the step that introduced the problem — do not try to fix upstream errors with downstream filters.