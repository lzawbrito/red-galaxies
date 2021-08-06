from api.cutouts import CutoutGenerator
from astropy.io import fits

PATH = '../../Clusters/A3911/combine_patch_color/z00-1111_whole.fits'
data, header = fits.getdata(PATH, header=True)


cg = CutoutGenerator(data, header)
cg.get_coords(0, 0)

cg.is_coord_in_image(341.535, -52.764)


