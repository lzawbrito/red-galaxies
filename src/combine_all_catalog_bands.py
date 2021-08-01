import sys 
import os 
import pandas as pd 
import io

CATALOG_DIRECTORY = 'files/clusters/'
OUTPUT_CSV = 'files/all_galaxies.csv'
BANDS = ['u', 'g', 'r', 'i', 'z']

# CODE BELOW TAKEN FROM api/catalogue_cleaning_pipeline.py
# -----------------------------------------------

EXTENDEDNESS_THRESHOLD = 0.9
CMODEL_MAG_THRESHOLD = 23
CMAG_DIFFERENCE_THRESHOLD = 0.8

def read_catalogue(band, fileName, filter_rg=True):
    """
    Opens csv catalogs and obtain desired columns, then stores them as a 
    dictionary, with the key being the record id.  
    """
    f = io.open(fileName, 'r')
    catalogue_values = {}
    column_indexes = {}
    line_read_count = 0
    while f.readable():
        line_read_count += 1
        line = f.readline()
    
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
        if filter_rg and band == 'r' and cmodel_mag > CMODEL_MAG_THRESHOLD:
            continue
        
        id = values[column_indexes['id']]
        row = {
            'id': values[column_indexes['id']],
            'ra': values[column_indexes['ra']],
            'dec': values[column_indexes['dec']],
            'extendedness': extendedness,
            'cmodel_mag': cmodel_mag
        }

        catalogue_values[id] = row
    return catalogue_values, line_read_count

def combine_columns(val):
    """
    Flatten the list of [band, ['ra', 'dec', ...]] into one 
    {'ra': ..., 'dec': ..., 'band_mag': ... }
    """
    (_, data) = val
    flattened_data = {'ra': data[0][1]['ra'], 'dec': data[0][1]['dec']}
    for t, d in data:
        flattened_data[t + '_mag'] = d['cmodel_mag']
        flattened_data[t + '_extendedness'] = d['extendedness']
    return flattened_data

def join_all_bands(catalogs):
    """
    Input as dictionary: 
        {
            'u': u_catalog,
            'g': g_catalog,
            'r': r_catalog,
            'i': i_catalog,
            'z': z_catalog
        } 
    """
    bands = list(catalogs.keys())
    start_band = bands[0]
    joined_bands = []

    for object_id in catalogs[start_band].keys():
        obj = catalogs[start_band][object_id]
        joined_object = {
            'ra': obj['ra'],
            'dec': obj['dec']
        }
        complete = True

        for band in bands:
            if not object_id in catalogs[band]:
                complete = False
                break

            joined_object[band + "_extendedness"] = catalogs[band][object_id]["extendedness"]
            joined_object[band + "_mag"] = catalogs[band][object_id]["cmodel_mag"]
        
        if complete:
            joined_bands.append(joined_object)

    return joined_bands

#-----------------------------------

galaxies = []
file_stems = []
total_searched = 0

for file in os.listdir(CATALOG_DIRECTORY):
	if file[-4:] == 'fits':
		continue
	stem = file[:-5]
	if stem in file_stems:
		continue
	file_stems.append(stem)

for stem in file_stems:
    print("Trying cluster: " + stem)	
    try:	
        catalogs = {}
        line_counts = 0
        for b in BANDS:
            current_file = stem + b + '.csv'
            current_catalog, line_count = read_catalogue(b, CATALOG_DIRECTORY + current_file,filter_rg=False)
            catalogs[b] = current_catalog
            line_counts += line_count
            print("Finished reading file: ", CATALOG_DIRECTORY + current_file)

        current_galaxies = join_all_bands(catalogs)
        galaxies += current_galaxies
        total_searched += line_counts
        print("Found more galaxies: ", len(current_galaxies))
        print("Total searched: " + str(total_searched))
    except Exception as e:
        print(f"Count not process {stem}: ", e)
		
print("Total number of galaxies found:", len(galaxies))

galaxies_df = pd.DataFrame(galaxies)

galaxies_df.to_csv(OUTPUT_CSV)





