from pyspark import SparkContext
import io
from operator import add

THREADS = 512
EXTENDEDNESS_THRESHOLD = 0.9
CMODEL_MAG_THRESHOLD = 23
CMAG_DIFFERENCE_THRESHOLD = 0.8

def read_catalogue(band, fileName, filter_rg=True):
    """
    Opens csv catalogs and obtain desired columns, then stores them as a 
    list.  
    """
    f = io.open(fileName, 'r')
    catalogue_values = []
    column_indexes = {}
    while f.readable():
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
        
        row = {
            'id': values[column_indexes['id']],
            'ra': values[column_indexes['ra']],
            'dec': values[column_indexes['dec']],
            'extendedness': extendedness,
            'cmodel_mag': cmodel_mag
        }

        catalogue_values.append(row)
    return catalogue_values

def get_tokenizer(token):
    return lambda x: (int(x['id']), [(token, x)])

def remove_solos(val, num_bands):
    """
    Remove columns that do not appear in at least `num_bands` bands. 
    """
    (_, lst) = val
    print(lst)
    return len(lst) >= num_bands

def cmag_mapper(val):
    """
    Calculates the difference in two band magnitudes. 
    """
    (_, ((_, value_1), (_, value_2))) = val
    
    cmag_difference = abs(value_1['cmodel_mag'] - value_2['cmodel_mag'])
    return (value_1, cmag_difference)

def remove_unworthy_differences(val):
    """
    Returns whether the difference in two cmags is significant.
    """
    (_, difference) = val
    return difference >= CMAG_DIFFERENCE_THRESHOLD

def map_to_value(val):
    (v, _) = val
    return v

def combine_columns(val):
    """
    Flatten the list of [band, ['ra', 'dec', ...]] into one 
    {'ra': ..., 'dec': ..., 'band_mag': ... }
    """
    (_, data) = val
    flattened_data = {'ra': data[0]['ra'], 'dec': data[0]['dec']}
    for t, d in data:
        flattened_data[t + '_mag'] = d['cmodel_mag']
        flattened_data[t + '_extendedness'] = d['extendedness']
    return flattened_data

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
                                 .filter(lambda x: remove_solos(x, 2)) \
                                 .map(cmag_mapper) \
                                 .filter(remove_unworthy_differences) \
                                 .map(map_to_value)

    return joined_result.collect()

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
    sc = SparkContext()
    bands = list(catalogs.keys())

    merged_tokens = []
    for band in bands:
        # records[band] = sc.parallelize()
        band_records = sc.parallelize(bands[band], THREADS)
        band_tokens = band_records.map(get_tokenizer(band))
        merged_tokens += band_tokens.collect()

    merged_tokens = sc.parallelize(merged_tokens, THREADS)
    joined_results = merged_tokens.reduceByKey(add) \
                                  .filter(lambda x: remove_solos(x, 5)) \
                                  .map(combine_columns)

    return joined_results.collect()


