sbatch --mem=32G --output=outputs/setup_training_data.out -n 32 -t 06:00:00 scripts/run_script.sh "src/setup_training_data.py files/cluster_images.csv files/all_galaxies_rad.csv files/all_galaxies_rad.csv files/training_data/ -threads 30 -unknown_samples 1000"

