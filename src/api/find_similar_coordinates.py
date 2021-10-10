from pyspark import SparkContext
from operator import add
THREADS = 512
ROUND_PLACES = 4

def find_similar_coordinates(coordinates_1, coordinates_2):
    """
    Inputs are assumed to be lists of dictionaries with values 'ra' and 'dec'
    """
    similar = []
    first_set = set()
    first_coords = coordinates_1[['ra','dec']].to_numpy()
    for ra_str, dec_str in first_coords:
        ra = round(float(ra_str), ROUND_PLACES)
        dec = round(float(dec_str), ROUND_PLACES)
        first_set.add((ra,dec))
   
    second_coords = coordinates_2[['ra','dec']].to_numpy()
    for ra_str, dec_str in second_coords:
        ra = round(float(ra_str), ROUND_PLACES)
        dec = round(float(dec_str), ROUND_PLACES)
        if (ra,dec) in first_set:
            similar.append((ra,dec))

    return similar


import pandas as pd
if __name__ == "__main__":
    test_catalogue = pd.read_csv("files/all_galaxies_rad.csv")
    test_huang = pd.read_csv('files/all_huang_candidates_formatted.csv')

    similar = find_similar_coordinates(test_huang, test_catalogue)

    print(similar)

