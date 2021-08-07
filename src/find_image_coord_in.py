from api.cutouts import CutoutGenerator
import pandas as pd 
from astropy.io import fits 
import traceback
import numpy as np
""

RA, DEC = 226.9381, 5.3823
FILENAME_ROUND_PLACES = 6
RELEVANT_BANDS = ['g','r','z']
IMAGE_CSV = 'files/known_cluster_images.csv'
OUTPUT_DIRECTORY = 'files/training_data/unknown/'
NUM_SAMPLES = 2000
CUTOUT_SIZE = 256

images_df = pd.read_csv(IMAGE_CSV)

# get one row per unique image
unique_clusters_df = images_df[images_df['band'] == 'z'].drop_duplicates(subset=['cluster'])

cgs = {}
for _, i in images_df.iterrows():
    data, header = fits.getdata(i['path'], header=True)
    cgs[i['path']] = CutoutGenerator(data, header)

cutouts = []

# keep track of broken files TODO figure out why they are broken
broken_files = set()
found_coords = set()
# total number of clusters inspected
n_clusters = 0
found_count = 0
for __, cluster in unique_clusters_df.iterrows():
    n_clusters += 1
    print(str(n_clusters) + "/" + str(len(unique_clusters_df)))

    # obtain CutoutGenerator object with which to test whether object 
    # is in image.
    test_cg = cgs[cluster['path']]
    print(test_cg.get_coords(0, 0))

    # Skip current cluster if file broken
    if cluster['path'] in broken_files:
        continue

    # Iterate over dataframe of coordinates

    # if coordinate has already been found, skip
    if (RA, DEC) in found_coords:
        continue
    try:
        # If coordinates are not in the image, skip 
        if not test_cg.is_coord_in_image(ra, dec):
            continue

        print('Coords ' + str(RA) + ', ' + str(DEC) + \
                ' found in cluster ' + str(cluster['path']) + "N: " + str(found_count))

        # # Obtain fits files corresponding to current cluster.
        # file_df = images_df[images_df['cluster'] == cluster['cluster']]
        
        # bands_dict = {
        #     "g": file_df[file_df['band'] == 'g']['path'].to_numpy()[0],
        #     "r": file_df[file_df['band'] == 'r']['path'].to_numpy()[0],
        #     "z": file_df[file_df['band'] == 'z']['path'].to_numpy()[0]
        # }

        # # Obtain cutouts of this object for each file corresponding to this cluster.
        # fits_data = np.zeros((3,CUTOUT_SIZE,CUTOUT_SIZE))
        # i = 0
        # for band in RELEVANT_BANDS:
        #     cg = cgs[bands_dict[band]]
        #     fits_data[i,:,:] = cg.get_cutout(ra, dec, (CUTOUT_SIZE, CUTOUT_SIZE))
        #     i += 1
        # hdu = fits.PrimaryHDU(fits_data)
        # hdu.writeto(OUTPUT_DIRECTORY + str(round(ra, FILENAME_ROUND_PLACES))+str(round(dec, FILENAME_ROUND_PLACES))+'.fits')
        found_count += 1

    except Exception as e:
        # Add file that excepts to list of broken files
        print("Exception: ", str(e))
        broken_files.add(cluster['path'])
        traceback.print_exc()
        break
                             
# possible mapreduce pipeline?
"""
Essentially a join 
- mapper - determine cluster coordinates are in. use above but don't iterate on coords, just have 
  coords as input to function 
- mapper - inner most for loop over file_df, use above mapper to determine 'cluster' column value 
- mapper - set coords to false if they don't appear in a cluster? like len(clusters) == 0?
- sc.collect() then just write contents of that list to a csv?
"""