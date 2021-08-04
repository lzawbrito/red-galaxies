import numpy as np
from astropy.io import fits
import os
import random

COMPRESSION = 4
NOTIFICATION_FREQUENCY = 100

def convert_to_pixel_data(fits_data, size):
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

def load_fits_data(DIR, sample_size_known, sample_size_unknown):
    data_result_pairs = []

    known_collected = 0

    for file in os.listdir(DIR + "known/"):
        if known_collected > sample_size_known:
            break
        if file.endswith(".fits"):
            data = fits.getdata(DIR + "known/" + file, header=False)
            data_result_pairs.append((convert_to_pixel_data(data, 256), [1]))
            known_collected += 1
            if known_collected % NOTIFICATION_FREQUENCY == 0:
                print(f"Found {known_collected} known lenses.")

    unknown_collected = 0
    for file in os.listdir(DIR + "unknown/"):
        if unknown_collected > sample_size_unknown:
            break
        if file.endswith(".fits"):
            data = fits.getdata(DIR + "unknown/" + file, header=False)
            data_result_pairs.append((convert_to_pixel_data(data, 256), [0]))
            unknown_collected += 1
            if unknown_collected % NOTIFICATION_FREQUENCY == 0:
                print(f"Found {unknown_collected} non lenses.")

    random.shuffle(data_result_pairs)

    fits_data = np.array([data[0] for data in data_result_pairs])
    expected_results = np.array([data[1] for data in data_result_pairs])

    return fits_data, expected_results


# TESTS 
if __name__ == '__main__':
    data, header = fits.getdata('/home/lzawbrito/PycharmProjects/csci1951a/csci1951a-final-project/data/DES-outputs/test.fits', header=True)
    assert len(np.shape(encode_fits(data))) == 1
    print('Tests passed!')
