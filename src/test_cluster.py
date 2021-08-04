from api.cutouts import CutoutGenerator 
from astropy.io import fits

PATH = '../../Clusters/A1606/combine_patch_color_output/A1606_u00-1111.fits'
data, header = fits.getdata(PATH2, header=True)
print(header)
cg = CutoutGenerator(data, header)
print(cg.is_coord_in_image(0, 0))

data, header = fits.getdata(PATH2, header=True)
print(header)
