import pandas as pd 
import numpy as np

"""
Written according to the following specification:
the goal is to find objects detected as fairly bright (mi or mz <22).  --remember smaller magnitudes mean brighter
but are very faint or missing (cmodel mag > 26) in u,g *and* r.

The red objects can be vetoed out by requiring mi - mz < 1 or 1.5
"""

CATALOG_DIR = 'files/all_galaxies.csv'
OUTPUT_DIR = 'files/distant_galaxies.csv'
REDDER_THRESH_MAG = 22
BLUER_THRESH_MAG = 26
REDDER_THRESH_DIFFERENCE = 24
MAG_FIELDS = ['u_mag', 'g_mag', 'r_mag', 'i_mag', 'z_mag']

# TODO make sure that we filter out entries that don't have every filter.

def all_true(l, func):
    """
    Returns true if `func` holds for every element of the given list `l`.
    """
    truth_value = True
    for i in l:
        truth_value = func(i) and truth_value
    return truth_value

assert all_true([-1, 2, 3], lambda x: x > 0) == False
assert all_true([], lambda x: x > 0) == True 
assert all_true([1, 2, 3], lambda x: x > 0) == True



def drop_dirty_data(df):
    """
    Drop rows with any empty magnitudes, or cells with value `inf`
    """
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df.dropna()

if __name__ == '__main__':

    df = pd.read_csv(CATALOG_DIR)
    drop_dirty_data(df)

    # Bright in red bands
    df = df[df.apply(lambda x: x['i_mag'] < REDDER_THRESH_MAG \
                                                and x['z_mag'] < REDDER_THRESH_MAG, axis=1)]

    # Dim in blue bands
    df = df[df.apply(lambda x: all_true([x['u_mag'], x['g_mag'], x['r_mag']], \
                                    lambda y: y > BLUER_THRESH_MAG), axis=1)]

    # Sufficiently small difference.
    df = df[df['i_mag'] - df['z_mag'] < REDDER_THRESH_DIFFERENCE]

    df.to_csv(OUTPUT_DIR)

