from api.legacy_survey import request_fits
from api.plot_fits_image import show_plot 
from astropy.io import fits
import os


FILE_PATH = "fits_test.fits" 
DEC = "+01.7490"
RA = "016.3319"
ZOOM = 0.14

request_fits("grz","dr9", RA, DEC, ZOOM, FILE_PATH)

data, header = fits.getdata(FILE_PATH, header=True)
print("Layers:", len(data))

show_plot(data[0])

os.remove(FILE_PATH)