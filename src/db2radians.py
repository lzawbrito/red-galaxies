import pandas as pd 
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='DES API Query')
parser.add_argument('-f', help='path to csv file', default='files/partial_all_galaxies.csv')
args =  parser.parse_args()

path = args.f

df = pd.read_csv(path)
df['ra'] = np.degrees(df['ra'])
df['dec'] = np.degrees(df['dec'])
df.to_csv(path[:-4] + '_rad.csv')


