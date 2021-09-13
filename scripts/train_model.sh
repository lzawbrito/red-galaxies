sbatch --mem=32G --output=outputs/train_model.out -n 4 -t 02:00:00 -p gpu --gres=gpu:1 run_gpu_script.sh src/api/resnet_model.py

