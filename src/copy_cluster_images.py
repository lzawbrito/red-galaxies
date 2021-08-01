from api.copy_tools import *
from shutil import copyfile
from os import listdir, path
from os.path import isdir, isfile, join 

dest_file= '../../dmi/red-galaxies/files/cluster_images.csv'
dest_dir = '../../dmi/red-galaxies/files/images/'
base_cluster_dir = '../../Clusters/'
catalog_dir = 'combine_patch_color_output'
catalog_alt_dir = 'combine_patch_color'
bands_to_copy = ['u', 'g', 'r', 'i', 'z']
 

#Obtain all cluster directories in Clusters.
dirs = []
try:
	dirs = [d for d in listdir(base_cluster_dir) if isdir(join(base_cluster_dir, d))]
	print('Successfully obtained ' + str(len(dirs)) + " cluster directories.")
except FileNotFoundError as e:
	print(e)
	print("Make sure you are running in ~/data/dmi/red-galaxies")


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


# empty contents of file 
open(dest_file, 'w').close()
for d in dirs:
	print("Current directory: " + d)
# Try `combine_patch_color_output`
	if isdir(join(base_cluster_dir, d, catalog_dir)):
		print("Trying: " + catalog_dir)
		get_by_bands(d, catalog_dir, 'fits', bands_to_copy, dest_file)
	# Try 'combine_patch_color'
	elif isdir(join(base_cluster_dir, d, catalog_alt_dir)):
		print("Trying: " + catalog_alt_dir)
		get_by_bands(d, catalog_alt_dir, 'fits', bands_to_copy, dest_file)
	else:
		print("No " + catalog_dir + " or " + catalog_alt_dir + " found in cluster " + d)


print("Successfuly copied " + str(file_len(dest_file)) + " catalogs.")

