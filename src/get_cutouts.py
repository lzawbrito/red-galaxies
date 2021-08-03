from api.cutouts import CutoutGenerator
import pandas as pd 
from astropy.io import fits 

IMAGE_CSV = 'files/cluster_images.csv'
RED_GALAXIES_CSV = 'files/all_red_galaxies.csv'

images_df = pd.read_csv(IMAGE_CSV)

# take head for now to avoid memory issues
all_red_galaxies_df = pd.read_csv(RED_GALAXIES_CSV).sample(n=100) 

# obtain ra, dec dataframe 
all_red_galaxies_coord_df = all_red_galaxies_df[['ra', 'dec']]

# get one row per unique 
unique_clusters_df = images_df[images_df['band'] == 'z'].drop_duplicates(subset=['cluster'])

cgs = {}
for _, i in images_df.iterrows():
    data, header = fits.getdata(i['path'], header=True)
    cgs[i['path']] = CutoutGenerator(data, header)

test_ra, test_dec = cgs[next(images_df.iterrows())[1]['path']].get_coords(50, 50)
test_coords_df = pd.DataFrame([00000000, test_ra, test_dec, 0, 0], 
                            colunms=['id','ra','dec','extendedness','cmodel_mag'])
all_red_galaxies_df.append(test_coords_df)


cutouts = []

for __, cluster in unique_clusters_df.iterrows():
    ra = coord['ra']
    dec = coord['dec']
    test_cg = cgs[cluster['path']]
    for _, coord in all_red_galaxies_coord_df.iterrows():
        try:
            if not test_cg.is_coord_in_image(ra, dec):
                continue
            print('Coords ' + str(coord['ra']) + ', ' + str(coord['dec']) + \
                  ' found in cluster ' + str(cluster['path']))
            file_df = images_df[images_df['cluster'] == cluster['cluster']]
            for ___, image in file_df.iterrows():
                cg = cgs[image['path']]
                data = cg.get_cutout(ra, dec)
                cutouts.append(((ra, dec), data))
        except Exception as e:
            continue 

# possible mapreduce pipeline?
"""
Essentially a join 
- mapper - determine cluster coordinates are in. use above but don't iterate on coords, just have 
  coords as input to function 
- mapper - inner most for loop over file_df, use above mapper to determine 'cluster' column value 
- mapper - set coords to false if they don't appear in a cluster? like len(clusters) == 0?
- sc.collect() then just write contents of that list to a csv?
"""




