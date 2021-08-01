from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from photutils.segmentation import *
from astropy.stats import sigma_clipped_stats
from astropy.convolution import Gaussian2DKernel
from astropy.stats import gaussian_fwhm_to_sigma
from plot_fits_image import show_plot, prepare_data


def clean_data(data, sigma=3.0):
    mean, median, std = sigma_clipped_stats(data, sigma=sigma)
    return data - median


def my_detect_sources(data, sigma_amp=3.0, nsigma=2.0):
    """Returns an astropy catalogue of the sources in FITS data."""
    threshold = detect_threshold(data, nsigma=nsigma)
    sigma = sigma_amp * gaussian_fwhm_to_sigma

    kernel = Gaussian2DKernel(sigma, x_size=len(data), y_size=len(data[0]))
    kernel.normalize()
    segm = detect_sources(data, threshold, npixels=5, filter_kernel=kernel)
    segm_deblend = deblend_sources(data, segm, npixels=5, filter_kernel=kernel, nlevels=32, contrast=0.001)

    cat = SourceCatalog(data, segm_deblend)

    return cat


def get_centroids(table):
    """Obtains the centroids of a table and returns them as a numpy matrix."""
    return np.transpose((table['xcentroid'], table['ycentroid']))


def srcs_in_annulus(coords, r1, r2, center=(0, 0)):
    """Counts the number of sources in the annulus of inner radius r1 and outer radius r2 centered at
    center. Considers the interval (r1, r2] with an open lower bound and closed upper bound."""
    count = 0
    for coord in coords:
        r_vec = (coord[0] - center[0], coord[1] - center[1])
        r = np.sqrt(r_vec[0] ** 2 + r_vec[1] ** 2)
        if r1 < r <= r2:
            count += 1
    return count


def annulus_area(r1, r2):
    """Returns the area of the annulus with the given inner and outer radii."""
    return np.pi * r2 ** 2 - np.pi * r1 ** 2


def source_density(data, dr, rstop, rstart=0, center=(0, 0)):
    srcs = get_centroids(my_detect_sources(data).to_table())

    radii = np.arange(rstart, rstop, dr)
    densities = []
    for r in list(radii):
        density = srcs_in_annulus(srcs, r, r + dr, center) / annulus_area(r, r + dr)
        densities.append(density)

    return radii, densities


data, header = fits.getdata("C:/Users/zawab/OneDrive/Documents/School/Research/Sample FITS Files/"
                            + "WFPC2u5780205r_c0fx.fits", header=True)

src_cat = my_detect_sources(data[0])
coords = get_centroids(src_cat.to_table())

print("Number of sources in annulus: {0}".format(srcs_in_annulus(coords, 0, 100, (100, 100))))


r, d = source_density(data[0], 10, 100, 0, center=(100, 100))


fig, ax = plt.subplots()
ax.plot(r, d, 'o')
plt.show()

