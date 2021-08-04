from api.cutouts import CutoutGenerator
import pandas as pd 
from astropy.io import fits 

IMAGE_CSV = 'files/known_cluster_images.csv'
RED_GALAXIES_CSV = 'files/all_galaxies_known_fits.csv'

images_df = pd.read_csv(IMAGE_CSV)

# take head for now to avoid memory issues
all_red_galaxies_df = pd.read_csv(RED_GALAXIES_CSV).sample(n=2000)

# obtain ra, dec dataframe 
all_red_galaxies_coord_df = all_red_galaxies_df[['ra', 'dec']]

# get one row per unique 
unique_clusters_df = images_df[images_df['band'] == 'z'].drop_duplicates(subset=['cluster'])

cgs = {}
for _, i in images_df.iterrows():
    data, header = fits.getdata(i['path'], header=True)
    print(header)
    cgs[i['path']] = CutoutGenerator(data, header)

# append test ra, dec coords to ensure script runs properly
if False:
    test_ra, test_dec = cgs[next(images_df.iterrows())[1]['path']].get_coords(50, 50)
    test_coords_df = pd.DataFrame([[test_ra, test_dec]], 
                            columns=['ra','dec'])
    all_red_galaxies_coord_df = all_red_galaxies_df.append(test_coords_df)

cutouts = []

# keep track of broken files TODO figure out why they are broken
broken_files = set()
found_coords = set()

# total number of clusters inspected
n_clusters = 0
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
    for _, coord in all_red_galaxies_coord_df.iterrows():
        ra = coord['ra']
        dec = coord['dec']

        # if coordinate has already been found, skip
        if (ra, dec) in found_coords:
            continue

        try:
            # If coordinates are not in the image, skip 
            if not test_cg.is_coord_in_image(ra, dec):
                continue

            print('Coords ' + str(coord['ra']) + ', ' + str(coord['dec']) + \
                  ' found in cluster ' + str(cluster['path']))

            # Obtain fits files corresponding to current cluster.
            file_df = images_df[images_df['cluster'] == cluster['cluster']]

            # Obtain cutouts of this object for each file corresponding to this cluster.
            for ___, image in file_df.iterrows():
                cg = cgs[image['path']]
                data = cg.get_cutout(ra, dec)
                cutouts.append([ra, dec, data])
            found_coords.add((ra, dec))

        except Exception as e:
            # Add file that excepts to list of broken files
            broken_files.add(cluster['path'])
            break
                             
print("Writing to file")
f = open('files/cutouts.csv', 'w')
f.write('ra,dec,data\n')
for r in cutouts:
    row = ""
    for c in r[:-1]:
        row += str(c) + ","
    row += str(r[-1])
    f.write(row)

# possible mapreduce pipeline?
"""
Essentially a join 
- mapper - determine cluster coordinates are in. use above but don't iterate on coords, just have 
  coords as input to function 
- mapper - inner most for loop over file_df, use above mapper to determine 'cluster' column value 
- mapper - set coords to false if they don't appear in a cluster? like len(clusters) == 0?
- sc.collect() then just write contents of that list to a csv?
"""


f.close()

