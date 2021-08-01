from api.legacy_survey import get_huang_candidates, request_fits
import random
from astropy.io import fits
from api.plot_fits_image import show_plot 
from api.encode_fits import encode_fits
import numpy as np
import os
import pandas as pd

SAVE_DIRECTORY = '../data/first_deliverable'
fits_outputs = []

# Generates example fits files and flattened input encodings from:

# Huang Data (5 Known Lenses)
HUANG_N = 5

huang_candidates = get_huang_candidates()
huang_sample = random.sample(huang_candidates, HUANG_N)
i = 0
for sample in huang_sample:
    out_file = f"{SAVE_DIRECTORY}/fits_files/Huang_{str(i)}.fits"
    request_fits("grz","dr9",sample['ra'], sample['dec'], 0.14, out_file)
    fits_outputs.append(out_file)
    i += 1


# Red Galaxies (5 Known Non-Lenses, since we cross referenced with known data)
RED_N = 5

red_candidates = pd.read_csv(f'{SAVE_DIRECTORY}/A3558_red_galaxies_partial.csv')
red_sample = random.sample(red_candidates.to_dict('records'), HUANG_N)
i = 0
for sample in red_sample:
    out_file = f"{SAVE_DIRECTORY}/fits_files/Red_{str(i)}.fits"
    request_fits("grz","dr9",sample['ra'], sample['dec'], 0.14, out_file)
    fits_outputs.append(out_file)
    i += 1

# Convert to vector encodings (to be use in ML model)

encoding_file = f"{SAVE_DIRECTORY}/encoded_fits.txt"
if os.path.isfile(encoding_file):
    os.remove(encoding_file)

f = open(encoding_file, "a")

for out_dir in fits_outputs:
    data, _ = fits.getdata(out_dir, header=True)
    f.write(np.array2string(encode_fits(data)) + '\n')

f.close()

# Display the fits file to the user to ensure accuracy

for out_dir in fits_outputs:
    data, _ = fits.getdata(out_dir, header=True)
    show_plot(data[1])