#!/bin/bash
#SBATCH -n 1

module load python/3.7.4
source ~/data/dmi/dmi/bin/activate
export PYTHONUNBUFFERED=TRUE
python $1
deactivate
