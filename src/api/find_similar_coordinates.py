from pyspark import SparkContext
from operator import add
THREADS = 128
ROUND_PLACES = 4

def get_tokenizer(token):
    return lambda x: ((round(float(x['ra']), ROUND_PLACES), round(float(x['dec']), ROUND_PLACES)), [(token, x)])

def mapper_1(val):
    (coords, locations) = val
    if len(locations) >= 2:
        ls = 0
        rs = 0
        for (token, _) in locations:
            if token == 'l':
                ls += 1
            else:
                rs += 1
        if ls > 0 and rs > 0:
            yield ('lr',[coords])
    else:
        (token, _) = locations[0]
        yield (token, [coords])

def find_similar_coordinates(coodinates_1, coordinates_2):
    """
    Inputs are assumed to be lists of dictionaries with values 'ra' and 'dec'
    """

    sc = SparkContext()

    candidates_1_records = sc.parallelize(coodinates_1, THREADS)
    candidates_2_records = sc.parallelize(coordinates_2, THREADS)
    candidates_1_records = candidates_1_records.map(get_tokenizer('l'))
    candidates_2_records = candidates_2_records.map(get_tokenizer('r'))

    merged_tokens = candidates_1_records.collect() + candidates_2_records.collect()

    merged_tokens = sc.parallelize(merged_tokens, THREADS)

    joined_result = merged_tokens.reduceByKey(add) \
                                 .flatMap(mapper_1) \
                                 .reduceByKey(add) \
                                 .collect()

    result = {token: value for (token, value) in joined_result}
    lr = result['lr'] if 'lr' in result else []
    l = result['l'] if 'l' in result else []
    r = result['r'] if 'r' in result else []

    return (lr,l, r)