sbatch --mem=16G --output=outputs/CMU_train_model.out -n 4 -t 02:00:00 -p gpu --gres=gpu:1 run_gpu_script.sh src/CMU_deeplens.py

