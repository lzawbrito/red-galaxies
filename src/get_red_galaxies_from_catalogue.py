from pyspark import SparkContext
import io
from operator import add
import pandas as pd
from api.catalogue_cleaning import read_catalogue

print("getting r coordinates")

r_bands = read_catalogue('r', '../../Clusters/A3558/read_merge_full_catalog_output/merge_A3558_001111_r.csv')

print("getting g coordinates")

g_bands = read_catalogue('g', '../../Clusters/A3558/read_merge_full_catalog_output/merge_A3558_001111_g.csv')

print("joining results")

joined = join_rg_bands(r_bands, g_bands)

df = pd.DataFrame(joined)

df.to_csv("A3559_red_galaxies.csv")
