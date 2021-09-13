from math import pi
from threading import local
from api.legacy_survey import request_fits
from api.plot_fits_image import prepare_data, show_plot
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

"""
The goal of this file is to figure out the proper scaling that we need between
the Legacy survey images and the images from our local dataset by comparing the 
pixel values at one known similar lens that is in both sets.
"""

RA = "226.9381"
DEC = "5.3823"
LEGACY_FILENAME = "data/comparison_legacy.fits"
LOCAL_FILENAME = "data/local_compare.fits"

"""Step 1: Get corresponding legacy survey file."""
request_fits("grz", "ls-dr9", RA, DEC, 0.3, LEGACY_FILENAME)
legacy_fits = fits.getdata(LEGACY_FILENAME)

"""Step 2: Get (or have) the existing file for the local candidate."""
local_fits = fits.getdata(LOCAL_FILENAME) 

"""Step 3: Apply whatever we can to make them as similar as possible (avoiding nuclear option)."""
local_fits = prepare_data(local_fits)

print(local_fits.size, legacy_fits.size)

show_plot(local_fits[0])
show_plot(legacy_fits[0])

print("Local: ", np.min(local_fits), np.max(local_fits))
print("Legacy: ", np.min(legacy_fits), np.max(legacy_fits))

"""Get quantifiable measure of fit."""
gradient, intercept, r_value, p_value, std_err = stats.linregress(legacy_fits.flatten(), local_fits.flatten())

print(gradient, intercept, r_value)

plt.plot(legacy_fits.flatten(), local_fits.flatten())
plt.show()