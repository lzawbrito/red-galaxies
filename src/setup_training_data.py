from api.cutouts import CutoutGenerator, group_clusters, save_cutouts_parallel
import pandas as pd 
from astropy.io import fits 
import traceback
import argparse
import numpy as np
from multiprocessing import Pool

# TODO 
""" 
- This still runs slowly, figure out why or parallelize.
  - is_coord_in_image is currently just a less than/greater than operation. 
- Check if some clusters are still erroring. 
"""

RELEVANT_BANDS = ['g','r','z']

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('cluster_csv', type=str,
                    help='path to the CSV file containing all of the found clusters')
parser.add_argument('known_lens_csv', type=str,
                    help='path to the known lens CSV file')
parser.add_argument('unknown_lens_csv', type=str,
                    help='path to the unknown lens CSV file')
parser.add_argument('output_directory', type=str,
                    help='the directory to create the folders `known` and `unknown` and place the found files into')
parser.add_argument('-known_samples', type=int, default=10,
                    help='number of samples to take from the known lenses')
parser.add_argument('-unknown_samples', type=int, default=20,
                    help='number of samples to take from the unknown lenses')
parser.add_argument('-cutout_size', type=int, default=256,
                    help='the size of the cutouts (in pixels)')
parser.add_argument('-threads', type=int, default=2,
                    help='number of threads to use for parallelization')
                
args = parser.parse_args()
print(args)

KNOWN_LENS_CSV = args.known_lens_csv
CLUSTER_CSV = args.cluster_csv
UNKNOWN_LENS_CSV = args.unknown_lens_csv
OUTPUT_DIRECTORY = args.output_directory
KNOWN_SAMPLES = args.known_samples
UNKNOWN_SAMPLES = args.unknown_samples
CUTOUT_SIZE = args.cutout_size
THREADS = args.threads

#------------------------------------------------------------
#  0. Load the paths to the cluster files and group them by band
#------------------------------------------------------------
print(f"Loading the clusters from: {CLUSTER_CSV}")

clusters_df = pd.read_csv(CLUSTER_CSV)

cluster_groups = group_clusters(clusters_df)

print(f"Found {len(cluster_groups)} total (distinct) clusters.")
#------------------------------------------------------------
#  1. Load and setup the local data
#------------------------------------------------------------

print(f"Loading {UNKNOWN_SAMPLES} sample from the local data.")

print(f"Reading unknown catalog from: {UNKNOWN_LENS_CSV}")
unknown_galaxies_df = pd.read_csv(UNKNOWN_LENS_CSV).sample(n=UNKNOWN_SAMPLES)

unknown_coordinates_df = unknown_galaxies_df[["ra", "dec"]]

print(f"Finding and saving files from local clusters to: {OUTPUT_DIRECTORY}")
print(f"Using {THREADS} threads")

save_cutouts_parallel(OUTPUT_DIRECTORY, cluster_groups, unknown_coordinates_df, THREADS, CUTOUT_SIZE)

print("Finished saving local cutouts.")