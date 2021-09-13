sbatch --mem=10G --output=$1.out -n 8 -t 00:10:00 run_script.sh $1
