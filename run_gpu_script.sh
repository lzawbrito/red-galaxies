#!/bin/bash
#SBATCH -n 1

module load python/3.7.4
module load cuda/11.1.1
module load cudnn/8.1.0
source ~/data/dmi/dmi/bin/activate
export PYTHONUNBUFFERED=TRUE
THEANO_FLAGS='device=gpu,floatX=float32,optimizer_including=cudann' python $1
deactivate
