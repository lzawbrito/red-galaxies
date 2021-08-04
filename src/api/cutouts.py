from astropy.coordinates.sky_coordinate import SkyCoord
from astropy.io import fits 
from astropy.wcs import WCS
import numpy as np 


class CutoutGenerator:
    def __init__(self, fits_data, fits_hdr):
        """
        Class used for obtaining cutouts of fits images. Determines 
        world coordinate system upon construction from fits header.
        """
        self.fits_data = fits_data
        self.fits_hdr = fits_hdr
        self.wcs = WCS(fits_hdr)
        self.dims = (len(fits_data[0]), len(fits_data))
        ra_lims = [self.get_coords(self.dims[0], self.dims[1])[0], self.get_coords(0, 0)[0]]
        ra_lims.sort()
        dec_lims = [self.get_coords(self.dims[0], self.dims[1])[1], self.get_coords(0, 0)[1]]
        dec_lims.sort()
        self.coord_bounds = {'ra_min': ra_lims[0],
                             'ra_max': ra_lims[1],
                             'dec_min': dec_lims[0],
                             'dec_max': dec_lims[1]}

    def get_cutout(self, ra, dec, dim=(64, 64)):
        """
        Obtains a cutout centered at the given RA, DEC coordinates.
        """
        if not(self.is_coord_in_image(ra, dec)):
            print("Coordinates outside image!")
            return 

        width = dim[0]
        height = dim[1]
        x, y = self.wcs.world_to_array_index(SkyCoord(ra, dec, unit="deg"))
        cutout = []
        try:
            for row in self.fits_data[y - int(height / 2):y + int(height / 2)]:
                cutout.append(row[x - int(width / 2):x + int(width / 2)])
        except IndexError:
            print('Error: object too close to edge of image.')
            # TODO try getting cutout that is exactly at edge?
        return cutout

    def is_coord_in_image(self, ra, dec):
        """
        Determines whether the given ra, dec coordinates are in the fits image. 
        """
        return self.coord_bounds['ra_min'] < ra < self.coord_bounds['ra_max'] \
           and self.coord_bounds['dec_min'] < dec < self.coord_bounds['dec_max']

    def get_coords(self, x, y):
        """
        Returns the ra, dec coordinates for the given pixel in the image. Note 
        that the methods returns the coordinates as floats, not as SkyCoord 
        objects.
        """
        coords = self.wcs.pixel_to_world(x, y)
        return coords.ra.degree, coords.dec.degree


# According to Dell'Antonio, the conversion from pixels to world 
# coordinates is:
#   Ra(x,y) = Crval1 + (x-Crpix1)*CD1_1 + (y-Crpix2)*CD1_2
#   Dec(x,y) = Crval2 + (x-crpix1)*Cd2_1+(y-crpix2)*cd2_2
if __name__ == '__main__':
    PATH = '../../data/A3558_g00-1111.fits'
    data, header = fits.getdata(PATH, header=True)

    w = WCS(header)
    coords = w.pixel_to_world(-1, 0)
    coords2 = w.world_to_pixel(SkyCoord(204.08830109, -33.24041172, unit="deg"))
    print(coords)
    print(coords2)
    

