
from matplotlib import colors
import matplotlib.pyplot as plt 
from filter_distant_galaxies import drop_dirty_data
from matplotlib.lines import Line2D
from numpy.core.fromnumeric import size, std 
import numpy as np 
import pandas as pd 


INPUT_DIRS = ['files/distant_galaxies.csv', 'files/all_galaxies.csv']
BANDS = ['u_mag', 'g_mag', 'r_mag', 'i_mag', 'z_mag']
BAND_NAMES = ['u (uv)','g (green)','r (red)','i (near ir)','z (infrared)']
OUTPUT_DIR = 'files/'
OUTPUT_NAME = 'distant_candidates.png'

x = np.arange(len(BANDS))
width = 0.35

df = drop_dirty_data(pd.read_csv(INPUT_DIRS[0]))
print(df)
means = df[BANDS].mean().to_numpy()
std_devs = df[BANDS].std().to_numpy()
object = np.array([26.287828966354304,26.608185526915754,27.35474939077231,21.674043110721,21.239574781518932])
scaled_means = np.power(object, 5) / 1000000


df2 = drop_dirty_data(pd.read_csv(INPUT_DIRS[1]))
means2 = df2[BANDS].mean().to_numpy()
std_devs2 = df2[BANDS].std().to_numpy()
scaled_means2 = np.power(means2, 5) / 1000000

X_axis = np.arange(len(BANDS))
  
plt.bar(X_axis - 0.2, scaled_means, 0.4, label = 'Distant Galaxies', yerr=std_devs)
plt.bar(X_axis + 0.2, scaled_means2, 0.4, label = 'All Galaxies', yerr=std_devs2)
  
plt.xticks(X_axis, BAND_NAMES)
plt.xlabel("Bands")
plt.ylabel("Average magnitude ^ 5 (millions)")
plt.title("Light Magnitudes of Distant Galaxies")
plt.legend()
plt.savefig(OUTPUT_DIR + OUTPUT_NAME)
plt.show()





