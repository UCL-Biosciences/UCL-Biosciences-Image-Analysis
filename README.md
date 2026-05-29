# UCL-Biosciences-Image Analysis
**Note**. This is a work-in-progress - some details and code need updating.

> **Who is this for?** PIs, postdocs, and PhD students who doing image analysis at UCL. We introduce image analysis, demonstrate some python-based workflows, and give instructions for running these workflows on Myriad, one of UCL's [High Performance Compute resources](https://github.com/UCL-Biosciences/Biosciences-Comp-Support/blob/main/UCL_comp_guides/high_performance_compute_at_UCL.md).

## Background
Analysing bioimage data is becoming increasingly complex. File sizes, the number of images and samples, and complex algorithms require specialised knowledge.

This repository demonstrates python-based image analysis in notebooks that run on [UCL high performance compute (HPC) systems](https://github.com/UCL-Biosciences/Biosciences-Comp-Support/blob/main/UCL_comp_guides/high_performance_compute_at_UCL.md). There are four notebooks that show:
1. segmenting touching nuclei using thresholding approaches
2. segmenting the same images using machine-learning models from cellpose
3. segmenting 3D images with multiple channels, including quantifying the number of substructures per cell
4. segmenting nuclei from multiple 3D images

## A reproducible workflow
These notebooks sit within a reproducible workflow, from data generation to data publishing. While the notebooks focus on data analysis, we are happy to discuss all of the below:
1. Data management - store and transfer data securely
2. Data analysis - robust and reproducible analyses
3. Data publishing - promote FAIR principles through good practice when publishing results

![Computational support for image analysis](docs/readme_files/Imaging-plan-20250716.svg)

Get in touch if you would like to discuss any part of a reproducible image analysis workflow: biosciences.imaging@ucl.ac.uk.

## Datasets
We will use a combination of [publicly available benchmark datasets](https://bbbc.broadinstitute.org/image_sets) and data generated within Biosciences to test and demonstrate pipelines.

See the [docs](https://github.com/UCL-Biosciences/UCL-Biosciences-Image-Analysis/blob/main/docs/data_used.txt) for explanation of data used.

### lif to tif
For some datasets, we may have converted the raw images from lif to tif using this [fiji macro](https://gist.github.com/lacan/16e12482b52f539795e49cb2122060cc). 

## Collaboration
We happily will have a team of people working on this project. It would be good for all contributors to read [this tutorial](https://vickysteeves.gitlab.io/collaborating-with-git/collaborating-with-git.html) before starting. More info [here](https://github.com/UCL-Biosciences/UCL-Biosciences-Image-Analysis/blob/main/docs/CONTRIBUTING.md).

### Environments
We use [conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) to manage the python libraries needed for the project. This is easier for users to set up, easier to share with others, and more reproducible. Setup instructions below. There are several environments that can be used for different notebooks.

We have a seprate one for image analysis without cellpose because it requires fewer packages and is easier to load: `envs/myriad_image_analysis.yaml` for myriad, `ADD_HERE_FOR_LOCAL` for local. This is sufficient for the first notebook that [segments nuclei via thresholding](https://github.com/UCL-Biosciences/UCL-Biosciences-Image-Analysis/blob/main/notebooks/01_segment_touching_nuclei.ipynb).

For notebooks 2, 3 and 4 that use cellpose, use `envs/myriad_cellpose.yaml` and `ADD_CELLPOSE_FOR_LOCAL`?

For the last two notebooks, which involve 3D segmentation, use `envs/myriad_3d` CHECK_THIS. For local, use this and make sure gpu is set to false.

## Project Structure
```
├── docs/           # docs explaining the repo in more detail
├── envs/           # environment files used to create conda environments
├── input_data/           # a few example images used by the notebooks
├── notebooks/           # Jupyter notebooks for development
└── output/              # Generated outputs (ignored by Git)
```
## Requirements

- Python 3.8+
- conda

## Setup and Usage
### Clone the Repository & Set Up (Locally or via VSC)
1. Open Visual Studio Code
2. If working on [UCL HPCs](https://github.com/UCL-Biosciences/Biosciences-Comp-Support/blob/main/UCL_comp_guides/high_performance_compute_at_UCL.md) remote SSH to Myriad (requires an older version of VSC, works with 1.94).
3. Clone the project repository into your workspace:

```
git clone https://github.com/UCL-Biosciences-Image-Analysis/UCL-Biosciences-Image-Analysis.git
cd Image-Analysis-Summer-Project
```
3. If on local machine, make sure conda is available (i.e. in your $PATH). If on Myriad, load Conda module:
```
module load python/miniconda3
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
```
4. Create the environment from the YAML file:
```
conda env create -f envs/myriad_image_analysis.yaml # or other - depends what you are doing. See `Environments` section above.
```
5. Activate the environment:
```
conda activate myriad_image_analysis # or the name of the env you want to use
```
6. Register the environment as a Jupyter kernel:
```
python -m ipykernel install --user --name=celltrack # change name as required
```

### Download the data
There is plenty of data on the [Broad Bioimage Benchmark Collection website](https://bbbc.broadinstitute.org/). 
This is just an example of 2D data (nuclei):

```
cd input_data
wget https://data.broadinstitute.org/bbbc/BBBC039/images.zip
unzip images.zip -d raw/
rm images.zip
```
This will extract the dataset into the raw/ folder, ready for segmentation. 

### Run the Notebook on Myriad via Open Ondemand

1. Go to Myriad's [Open OnDemand service](https://www.rc.ucl.ac.uk/docs/Supplementary/OnDemand/) and start a Jupyter notebook session. 1 CPU and 16GB RAM should be enough to work through most notebooks without cellpose. You can also request GPUs in Open OnDemand sessions, which speed up cellpose code.
2. Once the session starts, open the notebook. In the top right corner, select the kernel you set up following instructions above.
3. Go through the notebook.

## Resources
There are lots of great resources for learning image analysis. 

Robert Haase has a [huge resource](https://haesleinhuepf.github.io/BioImageAnalysisNotebooks/intro.html) covering a lot of key concepts. It includes a [large language model trained on image analysis](https://chat.openai.com/g/g-psAohb1OY-bio-image-analysis).

Or there is a similar set of [interactive notebooks](https://github.com/guiwitz/neubias_academy_biapy).

The EPFL Center for Imaging [awesome-scientific-image-analysis repo](https://github.com/EPFL-Center-for-Imaging/awesome-scientific-image-analysis) is a curated list of scientific image analysis resources and software tools.

More locally, the Crick has lots of good resources for both training and resources, e.g. [this course](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis/tree/main).

Globias has a [Call 4 Help website](https://call4help.let-your-data-speak.com/) where you can take image analysis problems and ask for help from a large community of experts.
# Image Segmentation With Cellpose-SAM

A modular pipeline for segmenting 2D microscopy images using Cellpose-SAM and validating segmentation quality.









