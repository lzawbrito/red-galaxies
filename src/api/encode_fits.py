from multiprocessing import Pool
import numpy as np
from astropy.io import fits
import os
import random

COMPRESSION = 4
NOTIFICATION_FREQUENCY = 100
LOWCUT_FILTER = 0.0001
HIGHCUT_FILTER = 0.01

def convert_to_pixel_data(fits_data, size):
    """
    Converts fits data from local files into the form that the model uses, and compresses if necessary.
    """
    new_size = int(size/COMPRESSION)
    new_image = np.zeros((new_size, new_size,3 ), dtype='float32')
    for k in range(3):
        for i in range(new_size):
            for j in range(new_size):
                start_i = i * COMPRESSION
                start_j = j * COMPRESSION
                end_i = start_i + COMPRESSION - 1
                end_j = start_j + COMPRESSION - 1
                new_image[i,j,k] = np.sum(fits_data[k,start_i:end_i,start_j:end_j])
    return new_image

def load_fits_data(data_directory, threads, image_size):
    """
    Loads fits files from a training directory `data_directory`. 
    Directory is expected to have subfolders `known` and `unknown`.
    """
    # Necessary so that multithreading can access this when it spawns off threads
    global read_fits

    def read_fits(fits_file):
        data = fits.getdata(fits_file, header=False)
        return convert_to_pixel_data(data, image_size)

    known_files = []
    for file in os.listdir(data_directory + "known/"):
        if file.endswith(".fits"):
            known_files.append(file)

    with Pool(processes=threads) as pool:
        known_collected = pool.map(read_fits, known_files)

    unknown_files = []
    for file in os.listdir(data_directory + "unknown/"):
        if file.endswith(".fits"):
            unknown_files.append(file)

    with Pool(processes=threads) as pool:
        unknown_collected = pool.map(read_fits, unknown_files)

    data_result_pairs = []
    for known in known_collected:
        data_result_pairs.append((known, [1]))
    for unknown in unknown_collected:
        data_result_pairs.append((unknown, [1]))

    random.shuffle(data_result_pairs)

    fits_data = np.array([data[0] for data in data_result_pairs])
    expected_results = np.array([data[1] for data in data_result_pairs])

    return fits_data, expected_results

def normalize_for_training(fits_data):
    """
    Takes a numpy array of `fits_data` and performs the necessary normalization for input into the model.
    """

    low_percentile = np.percentile(fits_data, 85)
    high_percentile = np.percentile(fits_data, 95)
    print(low_percentile, high_percentile)
    fits_data[fits_data < low_percentile] = 0
    fits_data[fits_data > high_percentile] = high_percentile

    fits_data = normalize_array(fits_data)
    return fits_data

def normalize_array(array):
    """
    Normalizes any numpy array to one with minimum value 0 and maximum value 1.
    """
    min = np.amin(array)
    max = np.amax(array)
    return (array - min) / (max - min)

