from api.legacy_survey import get_huang_candidates, request_fits
from astropy.io import fits
import os
from api.plot_fits_image import show_plot
import random


# Get the candidates from the 
candidates = get_huang_candidates()

print(candidates)

# Pick a random candidate and get it to make sure that we are being reasonable
# Not necessary
random_candidate = random.sample(candidates, 1)[0]
print(random_candidate)
FILE_PATH = "fits_test.fits" 

request_fits("grz","dr9", random_candidate.dec, random_candidate.ra, 0.14, FILE_PATH)

data, header = fits.getdata(FILE_PATH, header=True)
print("Layers:", len(data))

show_plot(data[0])
show_plot(data[1])
show_plot(data[2])

os.remove(FILE_PATH)