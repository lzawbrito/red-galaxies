from pyspark import SparkContext
import io
from operator import add

THREADS = 128
EXTENDEDNESS_THRESHOLD = 0.9
CMODEL_MAG_THRESHOLD = 23
CMAG_DIFFERENCE_THRESHOLD = 0.8

def read_catalogue(band, fileName):
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
        if band == 'r' and cmodel_mag > CMODEL_MAG_THRESHOLD:
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

def remove_solos(val):
    (_, lst) = val
    print(lst)
    return len(lst) >= 2

def cmag_mapper(val):
    (_, ((_, value_1), (_, value_2))) = val
    
    cmag_difference = abs(value_1['cmodel_mag'] - value_2['cmodel_mag'])
    return (value_1, cmag_difference)

def remove_unworthy_differences(val):
    (_, difference) = val
    return difference >= CMAG_DIFFERENCE_THRESHOLD

def map_to_value(val):
    (v, _) = val
    return v

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

    return joined_result.collect()