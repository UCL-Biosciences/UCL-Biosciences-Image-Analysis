# UCL-Biosciences-Image Analysis
**Note**. This is a work-in-progress - some details and code need updating.

> **Who is this for?** PIs, postdocs, and PhD students who doing image analysis at UCL. We introduce image analysis, demonstrate some python-based workflows, and give instructions for running these workflows on Myriad, one of UCL's [High Performance Compute resources](https://github.com/UCL-Biosciences/Biosciences-Comp-Support/blob/main/UCL_comp_guides/high_performance_compute_at_UCL.md).

## Background
Analysing bioimage data is becoming increasingly complex. File sizes, the number of images and samples, and complex algorithms require specialised knowledge.

Resources are required to support researchers handling complex datasets and analysis techniques.

In particular, many efficient and reproducible workflows are implemented in coding languages, such as python, which can be a barrier for researchers without coding experience.

Through this project, we will develop resources to help researchers run python-based image analysis workflows.

## A reproducible workflow
Our resources will demonstrate a robust and reproducible workflow, from data generation to data publishing. This covers three main themes:
1. Data management - store and transfer data securely
2. Data analysis - robust and reproducible analyses
3. Data publishing - promote FAIR principles through good practice when publishing results

![Computational support for image analysis](docs/readme_files/Imaging-plan-20250716.svg)

### Data Management
Transfer data and confirm with md5
Store on RDSS

### Data Analysis
Use scripting approach to generate repeatable, reproducible workflows.

Configure workflows without needing to change code. I.e. through config files. Make it accessible to non-coders.

Validate pipeline outputs by using test datasets with expected results.

Job scripts for running analyses on HPC clusters, again with minimal coding experience needed.

### Data Publishing
Demo of how to upload to archives, how to generate Zenodo DOI, what is needed for reproducibility (annotated code, environments etc).

## Image Analysis
We will generate resources for common analysis steps e.g. segmentation (2D and 3D), counting cells/nuclei, shape/size analysis, quantifying light intensity.

## Datasets
We will use a combination of [publicly available benchmark datasets](https://bbbc.broadinstitute.org/image_sets) and data generated within Biosciences to test and demonstrate pipelines.

There are a range of datasets on there, including [3D datasets](https://bbbc.broadinstitute.org/search/3D?) that look quite friendly ([e.g.](https://bbbc.broadinstitute.org/BBBC050). Please be clear about where data are downloaded from so others can reproduce the work. 

By running on different datasets, we will generate recommendations for a range of challenges and problems. Important as tutorials often only run on a single, simple test dataset.

### lif to tif
For some datasets, we may have converted the raw images from lif to tif using this [fiji macro](https://gist.github.com/lacan/16e12482b52f539795e49cb2122060cc). 

## Collaboration
We happily will have a team of people working on this project. It would be good for all contributors to read [this tutorial](https://vickysteeves.gitlab.io/collaborating-with-git/collaborating-with-git.html) before starting.

### Environments
To make sure we can all run the same code on our own machines, we will use [conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python). Once you have made an env and installed packages, export the list of packages with `conda env export --no-builds > requirements.txt`. This means anyone can recreate the envirornment with `conda env create -f requirements.txt` and we can all work happily and reproucibly! 

To make a conda env available as a jupyter notebook kernel: `python -m ipykernel install --user --name myenv --display-name "Python (myenv)"`

### Some important tips
- Clone the repository and make the conda environments first.
- We will organise tasks in the Issues tab. Share updates and questions there. Assign tasks to yourself if you are working on something.
- Don't commit directly to any of the branches above. These will be kept "clean" i.e. only include code that works.
- Make a new branch for any work you are doing. Be careful to branch _from_ the branch you want to work on.
- Keep branches focussed - one feature per branch. e.g. "adding myriad script". Try to only edit code relevant to the aim of the branch.
- Make your changes, check it all runs, push back to the dedicated branch on the repo, and open a Pull Request to merge with the relevant branch.
- Pull regularly to stay up to date
- Write clear messages so everyone can see what changes you've made

## Resources
There are lots of great resources for learning image analysis. 

Robert Haase has a [huge resource](https://haesleinhuepf.github.io/BioImageAnalysisNotebooks/intro.html) covering a lot of key concepts. It includes a [large language model trained on image analysis](https://chat.openai.com/g/g-psAohb1OY-bio-image-analysis).

Or there is a similar set of [interactive notebooks](https://github.com/guiwitz/neubias_academy_biapy).

The EPFL Center for Imaging [awesome-scientific-image-analysis repo](https://github.com/EPFL-Center-for-Imaging/awesome-scientific-image-analysis) is a curated list of scientific image analysis resources and software tools.

More locally, the Crick has lots of good resources for both training and resources, e.g. [this course](https://github.com/FrancisCrickInstitute/introduction-to-image-analysis/tree/main).

Globias has a [Call 4 Help website](https://call4help.let-your-data-speak.com/) where you can take image analysis problems and ask for help from a large community of experts.
# Image Segmentation With Cellpose-SAM

A modular pipeline for segmenting 2D microscopy images using Cellpose-SAM and validating segmentation quality.

## Project Structure

cellpose-segmentation-demo/

```
├── configs/              # Configuration files
│   └── params.yaml      # Main parameter settings
├── notebooks/           # Jupyter notebooks for development
├── scripts/             # Core Python modules (segmentation, validation, etc.)
├── jobs/                # HPC batch scripts
└── output/              # Generated outputs (ignored by Git)
```
## Requirements

- Python 3.8+
- conda
- configs/celltrack-env-myriad.yml

## Setup and Usage
### Clone the Repository & Set Up (Locally or via VSC)
1. Open Visual Studio Code via remote SSH to Myriad (requires an older version, works with 1.94).
2. Clone the project repository into your workspace:

```
git clone https://github.com/jdgilbert245/UCL-Biosciences-Image-Analysis.git
cd Image-Analysis-Summer-Project
git checkout image-segmentation-cellpose-demo # move to this branch of the repository
```
3. Load Conda module (example for Myriad):

```
module load python/miniconda3
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
```
4. Create the environment from the YAML file:
```
conda env create -f configs/celltrack-env-myriad.yml
```
5. Activate the environment:
```
conda activate celltrack
```
6. Register the environment as a Jupyter kernel:
```
python -m ipykernel install --user --name=celltrack
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

### Controlling settings with a configuration file
There is a config file in `configs/params.yaml` that defines the parameters for the Cellpose image segmentation pipeline, including input/output paths, testing options, segmentation settings, and validation controls.

- Input settings specify the source directory of TIFF image frames and the output folder for saving results.
- Testing mode allows downsampling and frame subsetting to quickly test the pipeline on a small portion of the dataset.
- Segmentation settings include Cellpose channel configuration and optional diameter hints for cell size. Cellpose-SAM is channel-order invariant, so you do not need to specify channel order explicitly.  
- Validation settings define how many images are randomly sampled for quality control (QC) visualisations and ROI tables.
- Advanced options include optional GPU acceleration and pixel size calibration.

This modular structure allows easy switching between full-scale analysis and quick testing, making it ideal for reproducible and configurable segmentation workflows.



### Run the Notebook on Myriad via Open Ondemand

1. Go to Myriad's [Open OnDemand service](https://www.rc.ucl.ac.uk/docs/Supplementary/OnDemand/) and start a Jupyter notebook session. 1 CPU and 32GB RAM should be enough to work through the notebook.
2. Once the session starts, open `notebooks/cellpose-segmentation.ipynb`. In the top right corner, select a kernel that has `celltrack` in the name.
3. Go through the notebook.










