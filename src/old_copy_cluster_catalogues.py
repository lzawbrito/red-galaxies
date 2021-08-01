from shutil import copyfile
from os import listdir, path
from os.path import isdir, isfile, join 

# NOTE: THIS FILE DEPRECATED. USE `copy_cluster_catalogues.py`

dest_dir = '../../dmi/red-galaxies/files/clusters/'
base_cluster_dir = '../../Clusters/'
catalog_dir = 'read_merge_full_catalog_output'
catalog_alt_dir = 'read_merge_full_catalog'


# Obtain all cluster directories in Clusters.
dirs = [d for d in listdir(base_cluster_dir) if isdir(join(base_cluster_dir, d))]
print('Successfully obtained ' + str(len(dirs)) + " cluster directories.")

num_catalogs = 0

def copy_catalogs(catalogs):
	"""
	Copies the list of catalogs provided to the base directory. 
	"""
	global num_catalogs
	for c in catalogs:
		copyfile(c, dest_dir + path.basename(path.normpath(c)))
		print("Current catalogue" + c)
		num_catalogs += 1

def get_green_red_bands(subdirectory, current_catalog_dir):
	"""
	Copies the merged catalogues of the `red` and `green` bands.
	First tries `catalog_dir` then `catalog_alt_dir`.
	"""
	current_dir = join(base_cluster_dir, subdirectory, \
		current_catalog_dir)
	

	files = [join(current_dir, f) for f in listdir(current_dir) \
		if isfile(join(current_dir, f))] 
	catalogs = [f for f in files \
			if 
			# Starts with `merge`
			   'merge_' in path.basename(path.normpath(f)) \
			# Ends with `_g.csv`  or `_r.csv`
			    and ('_g.csv' in f or '_r.csv' in f)]
	copy_catalogs(catalogs)


for d in dirs:
	print("Current directory: " + d)
	# Try `read_merge_full_catalog_output`
	if isdir(join(base_cluster_dir, d, catalog_dir)):
		print("Trying: " + catalog_dir)
		get_green_red_bands(d, catalog_dir)
	# Try 'read_merge_full_catalog'
	elif isdir(join(base_cluster_dir, d, catalog_alt_dir)):
		print("Trying: " + catalog_alt_dir)
		get_green_red_bands(d, catalog_alt_dir)
	else:
		print("No " + catalog_dir + " or " + catalog_alt_dir + " found in cluster " + d)
	

print("Successfuly copied " + str(num_catalogs) + " catalogs.")

