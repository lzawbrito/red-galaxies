import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture
from astropy.table import Table

def merge_tables(tables):
    """Merges two astropy tables into one."""
    empty_array = np.array([])
    merged_tables = Table(empty_array, names=tables[0].colnames)
    for table in tables:
        for row in table:
            merged_tables.add_row(list(row))
    return merged_tables


def my_detect_sources(data):
    """Detects stars using photutil's DAOStarFinder."""
    # FIXME a lot of false positives? Due to different channels being different images?
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    print("Mean:    {:.4f}\nMedian:  {:.4f}\nStdDev:  {:.4f}".format(mean, median, std))

    daofind = DAOStarFinder(fwhm=1.2, threshold=5.*std)
    sources = daofind(data - median)
    # sources = merge_tables([daofind(channel - median) for channel in data])

    for col in sources.colnames:
        sources[col].info.format = '%.8g'
    print(sources)
    print(type(sources))
    return np.transpose((sources['xcentroid'], sources['ycentroid']))


def prepare_data(data):
    """Prepares the given channel of the given data for plotting by
    shifting every value to > 0 and taking the logarithm."""
    channel_data = data

    # Obtain list of every value in data.
    flattened_data = []
    for l in channel_data:
        flattened_data.append(l)

    # Obtain minimum value from flattened data.
    min_value = np.amin(flattened_data)

    # Shift data by minimum.
    shifted_channel_data = []
    for l in channel_data:
        shifted_channel_data.append([i + np.abs(min_value) + 0.1 for i in l])

    return np.log(shifted_channel_data)


def show_plot(data, sources=[[0, 0]]):
    """Plots the given FITS data using matplotlib."""
    fig, ax = plt.subplots()
    ax.imshow(data)
    apertures = CircularAperture(sources, r=4)
    apertures.plot()
    plt.show()

def show_all_plots(all_data, sources=[[0, 0]]):
    """Plots all of the entries in the given FITS data using matplotlib."""
    fig, ax = plt.subplots()
    for data in all_data:
        ax.imshow(data)
    apertures = CircularAperture(sources, r=4)
    apertures.plot()
    plt.show()


