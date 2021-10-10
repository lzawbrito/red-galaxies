from astropy import wcs
from astropy.coordinates.sky_coordinate import SkyCoord
from astropy.io import fits 
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
import astropy.units as u
import numpy as np 
from multiprocessing import Pool
from os.path import isfile

FILENAME_ROUND_PLACES = 8

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
        pos = SkyCoord(ra=ra * u.degree, dec=dec * u.degree)
        cutout = Cutout2D(self.fits_data, pos, dim, wcs=self.wcs)
        
        return cutout.data

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


def group_clusters(clusters_df):
    """
    Given a pandas dataframe of cluster location and bands, groups them by which cluster they belong to and aligns the bands:
    
    Outputs: list of dictionaries of the form: ("g": g_file, "r": r_file, "z": z_file)
    """
    unique_clusters_df = clusters_df[clusters_df['band'] == 'z'].drop_duplicates(subset=['cluster'])

    # cluster_groups: list of dictionaries of the form: ("cluster": cluster_name, "g": g_file, "r": r_file, "z": z_file)
    cluster_groups = []
    for __, cluster in unique_clusters_df.iterrows():
        file_df = clusters_df[clusters_df['cluster'] == cluster['cluster']]
                
        bands_dict = {
            "cluster": cluster["cluster"],
            "g": file_df[file_df['band'] == 'g']['path'].to_numpy()[0],
            "r": file_df[file_df['band'] == 'r']['path'].to_numpy()[0],
            "z": file_df[file_df['band'] == 'z']['path'].to_numpy()[0]
        }
        cluster_groups.append(bands_dict)
    return cluster_groups


def save_cutouts_parallel(output_path, grouped_clusters, coordinates, threads, cutout_size):
    """
    Looks for the cutouts for the given `coordinates` across cluster files from `grouped_clusters`. 
    Saves them into a folder `output_path`, and parallelizes over `threads` threads. 
    """
    # This is ugly, but otherwise it doesn't seem like multiprocessing supports this sort of currying.
    global search_cluster_lambda

    def search_cluster_lambda(cluster):
        search_cluster(cluster, coordinates, output_path, cutout_size)

    with Pool(processes=threads) as pool:
        return pool.map(search_cluster_lambda, grouped_clusters)

def search_cluster(cluster, coordinates, output_path, cutout_size):
    print(f"Searching cluster {cluster['cluster']}")
    g_data, g_header = fits.getdata(cluster['g'], header=True)
    g_generator = CutoutGenerator(g_data, g_header)

    r_data, r_header = fits.getdata(cluster['r'], header=True)
    r_generator = CutoutGenerator(r_data, r_header)

    z_data, z_header = fits.getdata(cluster['z'], header=True)
    z_generator = CutoutGenerator(z_data, z_header)

    for _, coord in coordinates.iterrows():
        ra = coord['ra']
        dec = coord['dec']

        if not g_generator.is_coord_in_image(ra, dec):
                continue
        
        filename = f"{output_path}{str(round(ra, FILENAME_ROUND_PLACES))}_{str(round(dec, FILENAME_ROUND_PLACES))}.fits"

        if isfile(filename):
            # This was already found by another one of the files (overlap)
            continue
        
        fits_data = np.zeros((3,cutout_size,cutout_size))
        fits_data[0,:,:] = g_generator.get_cutout(ra, dec, (cutout_size, cutout_size))
        fits_data[1,:,:] = r_generator.get_cutout(ra, dec, (cutout_size, cutout_size))
        fits_data[2,:,:] = z_generator.get_cutout(ra, dec, (cutout_size, cutout_size))

        hdu = fits.PrimaryHDU(fits_data)
        hdu.writeto(filename)
    

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
    

