from astropy.io import fits
import numpy as np
import argparse 

def parse_args():
	parser = argparse.ArgumentParser(description='Print the contents of a fits file.')
	parser.add_argument('-f', help="Path to .fits file", default='../../A1767.fits')
	return parser.parse_args()

#This is what I did in `show_fits` in the repo.
args = parse_args()
file_path = args.f
data, header = fits.getdata(file_path, header=True)
print("--------------- Header ---------------")
print(str(header).replace(' ', ''))
print("--------------- Data -----------------")
print(np.array(data))


# The below doesn't seem to be working for some reason. I think we might be overcomplicating things. See above.
#fits_image_filename = fits.util.get_testdata_filepath('../../A1767.fits')

#hdul = fits.open(fits_image_filename)

#hdul.info()

#hdul.close()
