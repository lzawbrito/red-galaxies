from api.cutouts import CutoutGenerator
import pandas as pd 
from astropy.io import fits 

IMAGE_CSV = 'files/cluster_images.csv'
RED_GALAXIES_CSV = 'files/all_red_galaxies.csv'

images_df = pd.read_csv(IMAGE_CSV)

# take head for now to avoid memory issues
all_red_galaxies_df = pd.read_csv(RED_GALAXIES_CSV).head(n=100) 

# obtain ra, dec dataframe 
all_red_galaxies_coord_df = all_red_galaxies_df[['ra', 'dec']]

# get one row per unique 
unique_clusters_df = images_df.drop_duplicates(subset=['cluster'])

for _, coord in all_red_galaxies_coord_df.iterrows():
    for __, cluster in unique_clusters_df.iterrows():
        data, header = fits.getdata(cluster['path'])
        cg = CutoutGenerator(data, header)
        if not cg.is_coord_in_image(coord['ra'], coord['dec']):
            continue
        
        print('Coords ' + str(coord['ra']) + ', ' + str(coord['dec']) + \
              ' found in cluster ' + str(cluster['path']))


