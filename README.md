# Image Segmentation With Cellpose-SAM

A modular pipeline for segmenting time-lapse microscopy images using Cellpose and validating segmentation quality.

## Project Structure

cellpose-segmentation-demo/

```
├── config/              # Configuration files
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
1. Open Visual Studio Code on your local machine or via remote SSH to Myriad.
2. Clone the project repository into your workspace:

```
git clone git@github.com:jdgilbert245/Image-Analysis-Summer-Project.git
cd your-project
git checkout image-segmentation-cellpose-demo # move to this branch of the repository
```
3. Load Conda module (example for Myriad):

```
module load python/miniconda3
source $UCL_CONDA_PATH/etc/profile.d/conda.sh
```
4. Create the environment from the YAML file:

`conda env create -f config/celltrack-env-myriad.yml`

5. Activate the environment:

`conda activate celltrack-env-myriad`

6. Register the environment as a Jupyter kernel:

`python -m ipykernel install --user --name=celltrack-env-myriad`

### Run the Notebook on Myriad via Open Ondemand

1. Go to Myriad's [Open OnDemand service](https://www.rc.ucl.ac.uk/docs/Supplementary/OnDemand/) and start a Jupyter notebook session. 1 CPU and 32GB RAM should be enough to work through the notebook.
2. Once the session starts, open `notebooks/cellpose-segmentation.ipynb`. In the top right corner, select a kernel that has `celltrack-env-myriad` in the name.
3. Go through the notebook.

###










