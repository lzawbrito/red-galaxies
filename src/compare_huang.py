from api.find_similar_coordinates import find_similar_coordinates
from api.catalogue_cleaning_pipeline import read_catalogue
import pandas as pd

"""
This script compares the known lense candidates that were found by Huang with the 
"""

test_catalogue = pd.read_csv("files/all_galaxies.csv")
test_huang = pd.read_csv('files/all_huang_candidates_formatted.csv')

test_huang_dict = test_huang.to_dict('records')
test_catalogue_dict = test_catalogue.to_dict('records')

(a,b,c) = find_similar_coordinates(test_huang_dict, test_catalogue_dict)

print(a)
print(len(a),len(b),len(c))
