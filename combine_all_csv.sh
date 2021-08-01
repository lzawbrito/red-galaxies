sbatch --mem=32G --output=outputs/combine_all_csv.out -n 4 -t 4:00:00 run_script.sh src/combine_all_catalog_bands.py

