sbatch --mem=8G --output=outputs/setup_training_data.out -n 4 -t 06:00:00 run_script.sh src/setup_training_data.py files/cluster_images.csv files/all_galaxies.csv files/all_galaxies.csv files/training_data/ -threads 3 

