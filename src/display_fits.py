from api.plot_fits_image import show_plot 
from astropy.io import fits
import numpy as np 

FILE_PATH = '/home/lzawbrito/PycharmProjects/csci1951a/csci1951a-final-project/data/DES-outputs/2bea7e6639814fc8a3b0571988ccae2f/DES0105+0126/DESJ010519.6560+014456.4000/DESJ010519.6560+014456.4000_i.fits'
data, header = fits.getdata(FILE_PATH, header=True)
print(f"Layers: {len(data)}\tShape: {np.shape(data)}")


show_plot(data)