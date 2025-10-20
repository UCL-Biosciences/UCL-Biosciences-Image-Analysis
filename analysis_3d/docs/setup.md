# Setup

Brief setup instructions are given in the respective readmes. Here we collect some additional setup info.

## Installation
### Conda Environments
Complex conda environments can be hard to install. Particularly when working on e.g. HPCs with specific requirements of their own. Lada did great work finding the right packages to run the 3D segmentation script. It should be possible to recreate the env using `conda env create -f 3d_image_segm_env_hpc.yml -n 3d-image-segm-env-hpc`.

Here are some notes on the installation process (from this [issue](https://github.com/jdgilbert245/UCL-Biosciences-Image-Analysis/issues/17#issuecomment-3258414626)): 

I updated the conda envs for both local and HPC, they both worked fine after I tried to recreate them from files. The instructions are now in README, and the note about the numpy version is in the dependencies section. Other than that, I am not too sure what other packages could be an issue, unless the environment is created from scratch on Myriad (in which case, I tried to do the sequence of module loadings below to successfully install cellpose and stardist (run `pip install "numpy>=1.24,<2.0"` before attempting stardist).

In case the error with building the wheel for ml-dtypes arises during pip install stardist, I tried to load an existing tensorflow module with the sequence (from Myriad q&a website):
`module unload compilers mpi gcc-libs`
`module load gcc-libs/10.2.0`
`module load python/3.9.6-gnu-10.2.0`
`module load cuda/11.2.0/gnu-10.2.0`
`module load cudnn/8.1.0.77/cuda-11.2`
`module load tensorflow/2.11.0/gpu`

After that stardist was installed correctly. However, when trying to `conda install ipykernel` later, I needed to run the `export PYTHONPATH=$CONDA_PREFIX/lib/python3.10/site-packages:$PYTHONPATH` to locate Python, after which ipykernel installed and started working to register a new environment. 

I am not sure what exactly made the trick, but that worked for me to create a clean hpc environment.


### Config Files

#### Input

#### Output


#### Settings
