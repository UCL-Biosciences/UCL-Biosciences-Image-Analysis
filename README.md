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
1. Open Visual Studio Code via remote SSH to Myriad (requires an older version, works with 1.94).
2. Clone the project repository into your workspace:

```
git clone git@github.com:jdgilbert245/Image-Analysis-Summer-Project.git
cd Image-Analysis-Summer-Project
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

### Download the data
There is plenty of data on the [Broad Bioimage Benchmark Collection website](https://bbbc.broadinstitute.org/). You could e.g.

```
mkdir -p input_data
cd input_data
wget https://data.broadinstitute.org/bbbc/BBBC035/BBBC035_v1_dataset.zip
unzip BBBC035_v1_dataset.zip -d raw/
rm BBBC035_v1_dataset.zip
```
This will extract the dataset into the data/raw/ folder, ready for segmentation. You will need to check they are in the expected format and confirm the paths are correct in the Jupyter notebooks and corresponding config files.

### Controlling settings with a configuration file
There is a config file in `config/params.yaml` that defines the parameters for the Cellpose image segmentation pipeline, including input/output paths, testing options, segmentation settings, and validation controls.

- Input settings specify the source directory of TIFF image frames and the output folder for saving results.
- Testing mode allows downsampling and frame subsetting to quickly test the pipeline on a small portion of the dataset.
- Segmentation settings include Cellpose channel configuration and optional diameter hints for cell size.
- Validation settings define how many images are randomly sampled for quality control (QC) visualisations and ROI tables.
- Advanced options include optional GPU acceleration and pixel size calibration.

This modular structure allows easy switching between full-scale analysis and quick testing, making it ideal for reproducible and configurable segmentation workflows.

### Run the Notebook on Myriad via Open Ondemand

1. Go to Myriad's [Open OnDemand service](https://www.rc.ucl.ac.uk/docs/Supplementary/OnDemand/) and start a Jupyter notebook session. 1 CPU and 32GB RAM should be enough to work through the notebook.
2. Once the session starts, open `notebooks/cellpose-segmentation.ipynb`. In the top right corner, select a kernel that has `celltrack-env-myriad` in the name.
3. Go through the notebook.










