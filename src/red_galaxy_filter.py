import pandas as pd


red_galaxy_df =  pd.read_csv('~/data/Clusters/A3558/read_merge_full_catalog_output/merge_A3558_001111_g.csv')

red_galaxy_df = red_galaxy_df[red_galaxy_df['fp_base_ClassificationExtendedness_value'] < 0.9]

print(red_galaxy_df)

