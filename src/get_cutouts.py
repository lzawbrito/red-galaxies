from api.cutouts import CutoutGenerator
import pandas as pd 
from astropy.io import fits 

IMAGE_CSV = 'files/cluster_images.csv'

images_df = pd.read_csv(IMAGE_CSV)
unique_clusters = images_df['cluster'].unique()

