#!/bin/bash -l

# Request wallclock time (format hours:minutes:seconds).
#$ -l h_rt=1:00:0

# Request RAM (must be an integer followed by M, G, or T)
#$ -l mem=32G

# Request TMPDIR space (default is 10 GB - remove if cluster is diskless)
#$ -l tmpfs=15G

# Set the name of the job.
#$ -N cellpose-segmentation

# Set the working directory to somewhere in your scratch space.  
#  This is a necessary step as compute nodes cannot write to $HOME.
#$ -wd /home/ucsagil/Scratch/image-analysis/cellpose-segmentation-demo

# Your work should be done in $TMPDIR 
cd $TMPDIR

### load conda module and env
module load python/miniconda3/
source $UCL_CONDA_PATH/etc/profile.d/conda.sh 

conda activate celltrack

### set dir path
proj_dir = /home/ucsagil/Scratch/image-analysis/cellpose-segmentation-demo

python main.py --config ${proj_dir}/config/params.yaml
