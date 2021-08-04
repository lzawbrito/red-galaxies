from api.cutouts import CutoutGenerator
from astropy.io import fits 
from astropy.coordinates import Angle
from api.plot_fits_image import show_plot, prepare_data
# -31.49548°
#  12.4658°
RA, DEC = 201.9783, -31.4922
print(RA, DEC)
PATH = '../../../A3558_g00-1111.fits'

data, header = fits.getdata(PATH, header=True)
cg = CutoutGenerator(data, header)
c = cg.get_cutout(RA, DEC, dim=(1000, 1000))
show_plot(prepare_data(c))
print(cg.is_coord_in_image(RA, DEC))




