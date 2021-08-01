import sys
import os

import pandas as pd

CATALOG_DIRECTORY = 'files/clusters/'
OUTPUT_CSV = 'files/all_red_galaxies.csv'

# Code copied from api/catalogue_cleaning_pipeline.py
#--------------------------------------------------------

from pyspark import SparkContext
import io
from operator import add

SparkContext.setSystemProperty('spark.driver.memory', '16g')
SparkContext.setSystemProperty('spark.executor.memory', '8g')
THREADS = 512
EXTENDEDNESS_THRESHOLD = 0.9
CMODEL_MAG_THRESHOLD = 23
CMAG_DIFFERENCE_THRESHOLD = 0.8

def read_catalogue(band, fileName):
    f = io.open(fileName, 'r')
    catalogue_values = []
    column_indexes = {}
    total_searched = 0
    while f.readable():
        line = f.readline()
        total_searched += 1
        values = line.split(',')

        if len(values) <= 2:
           break

        if values[0] == 'fp_id':
            # Header row
            column_indexes['id'] = values.index('fp_id')
            column_indexes['extendedness_value'] = values.index('fp_base_ClassificationExtendedness_value')
            column_indexes['cmodel_mag'] = values.index('CModel_Mag')
            column_indexes['ra'] = values.index('fp_coord_ra')
            column_indexes['dec'] = values.index('fp_coord_dec')
            continue

        extendedness = float(values[column_indexes['extendedness_value']])
        if extendedness < EXTENDEDNESS_THRESHOLD: 
            continue

        cmodel_mag = float(values[column_indexes['cmodel_mag']])
        if band == 'r' and cmodel_mag > CMODEL_MAG_THRESHOLD:
            continue
        
        row = {
            'id': int(values[column_indexes['id']]),
            'ra': values[column_indexes['ra']],
            'dec': values[column_indexes['dec']],
            'extendedness': extendedness,
            'cmodel_mag': cmodel_mag
        }
	
        catalogue_values.append(row)
    return catalogue_values, total_searched

def get_tokenizer(token):
    return lambda x: (int(x['id']), [(token, x)])

def remove_solos(val):
    return len(val[1]) >= 2

def cmag_mapper(val):
    return (val[1][0][1], abs(val[1][0][1]['cmodel_mag'] - val[1][1][1]['cmodel_mag']))

def remove_unworthy_differences(val):
    return val[1] >= CMAG_DIFFERENCE_THRESHOLD

def map_to_value(val):
    return val[0]

def join_rg_bands(r_bands, g_bands):

    sc = SparkContext()

    g_records = sc.parallelize(g_bands, THREADS)
    r_records = sc.parallelize(r_bands, THREADS)

    # Run the mapreduce pipeline 

    g_tokens = g_records.map(get_tokenizer('g'))
    r_tokens = r_records.map(get_tokenizer('r'))

    merged_tokens = g_tokens.collect() + r_tokens.collect()

    merged_tokens = sc.parallelize(merged_tokens, THREADS)

    joined_result = merged_tokens.reduceByKey(add) \
                                 .filter(remove_solos) \
                                 .map(cmag_mapper) \
                                 .filter(remove_unworthy_differences) \
                                 .map(map_to_value)

    
    result = joined_result.collect()
    sc.stop()
    return result

#-------------------------------------------------------

MAX_IN_ROUND = 1000000
all_red_galaxies = []
file_pairs = []
used_files = set()
total_searched = 0

for file in os.listdir(CATALOG_DIRECTORY):
	if file in used_files:
		continue
	used_files.add(file)
	band = file[-5]
	other_band = 'g' if band == 'r' else 'r'	
	other_file_name = file[:-5] + other_band + file[-4:]
	used_files.add(other_file_name)
	if band == 'r':
		file_pairs.append((file,other_file_name))
	else:
		file_pairs.append((other_file_name, file))
		
print("Number of catalogs found: ", len(file_pairs))
for r_band_file, g_band_file in file_pairs:		
	print("Trying files: ", r_band_file, g_band_file)
	try:

		r_band, r_count = read_catalogue('r', CATALOG_DIRECTORY + r_band_file)
		g_band, g_count = read_catalogue('g', CATALOG_DIRECTORY + g_band_file)
			
		print("Number of r,g records: ", r_count, g_count)
		# rounds = int(len(r_band) / MAX_IN_ROUND) + 1
		# print("Doing Rounds: ", rounds)

		
			# print("Min and Max: ", minimum, maximum)
			# range_filter = lambda x: x['id'] < maximum and x['id'] > minimum
			# r_band_limited = list(filter(range_filter, r_band))
			# g_band_limited = list(filter(range_filter, g_band))

			# print("Limited bands: ", len(r_band_limited), len(g_band_limited))
		red_galaxies = join_rg_bands(r_band, g_band)
		print("Found Red Galaxies: ", len(red_galaxies))
		all_red_galaxies += red_galaxies
		total_searched += r_count + g_count
		print("New total searched: ", total_searched)

	except Exception as e:
		print('Could not process files:', r_band_file, g_band_file)
		print("Error: ", e)
		
print("Total number of red galaxies found:", len(all_red_galaxies))
galaxies_df = pd.DataFrame(all_red_galaxies)

galaxies_df.to_csv(OUTPUT_CSV)



