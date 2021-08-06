from shutil import copyfile
from os import listdir, path
from os.path import isdir, isfile, join 


num_catalogs = 0
base_cluster_dir = '../../Clusters/'

def is_one_in(l, iterable, func):
	"""
	Check if at least one of the elements in a list is in an iterable/string, using func to check whether 
	said element is considered to be equal. 
	"""
	is_in = False
	for i in l:
		is_in = is_in or func(i, iterable)
	return is_in
assert is_one_in(['a', 'b', 'c'], 'a', lambda x, y: x in y) == True 
assert is_one_in(['a', 'b', 'c'], 'z', lambda x, y: x in y) == False
assert is_one_in(['a', 'b', 'c'], 'a', lambda x, y: x + '.csv' in y) == False


def is_correct_format(filename, extension, bands=None):
	"""
	Determines whether the given file has the correct format. 
	"""
	correct_band = True
	if bands:
			correct_band = is_one_in(bands, filename, lambda x, y: x + '.' in y) \
							or is_one_in(bands, filename, lambda x, y: '_' + x + '_' in y)
	correct_extension = filename.split('.')[-1] == extension
	return correct_band and correct_extension


def add_to_copy_queue(rows, dest_file):
	global num_catalogs

	queue = open(dest_file, 'a')
	for r in rows:
		print("Appending row " + str(r) + " to " + dest_file)


		# append current cluster to file
		if not r[1] == '.':
			csv_row = ""
			for i in r:			
				csv_row += i 
				if not r.index(i) == len(r) - 1:
					csv_row += ','
			queue.write(csv_row + '\n')
			num_catalogs += 1
	queue.close()


def copy_catalogs(catalogs, cluster):
	"""
	Copies the list of catalogs provided to the base directory. 
	"""
	global num_catalogs

	for c in catalogs:
		new_filename = path.basename(path.normpath(c))
		if cluster not in new_filename:
			new_filename = cluster + new_filename
		print("Copying catalog " + c + " to " + join(dest_dir, new_filename))
		copyfile(c, join(dest_dir, new_filename))
		num_catalogs += 1


def get_largest_size_catalog(cats, band):
	largest = ''
	largest_size = 0
	for c in cats:
		size = path.getsize(c)
		if size > largest_size and '_' + band in path.basename(path.normpath(c)):
			largest_size = size
			largest = c
	return path.split(largest)[0], path.basename(path.normpath(largest))
	

def get_largest_range_catalogs(cats):
	"""
	#Obtains the largest range catalogs in the list of catalogs.
	"""
	sizes = ['001111', '0to11',]
	files_to_keep = []
	for c in cats:
		for s in sizes:
			bn = path.basename(path.normpath(c))
			if s in bn and sizes.index(s) <= sizes.index(largest_size):
				largest_size = s
		
	for c in cats:
		bn = path.basename(path.normpath(c))
		if largest_size in bn:
			files_to_keep.append(c)
	
	return files_to_keep


def get_by_bands(subdirectory, current_catalog_dir, file_extension, bands, dest_file):
	"""
	Copies the merged catalogues of the specified bands.
	First tries `catalog_dir` then `catalog_alt_dir`.
	"""

	current_dir = join(base_cluster_dir, subdirectory, \
		current_catalog_dir)
	

	files = [join(current_dir, f) for f in listdir(current_dir) \
		if isfile(join(current_dir, f))] 

	catalogs = [f for f in files if is_correct_format(path.basename(path.normpath(f)), file_extension)]
	basedir, largest_filename = get_largest_size_catalog(catalogs, bands[1])
	# TODO below does not work becuse some catalogues are missing `u` band for some reason??
	if not(largest_filename == ''):
		largest_catalogs = [(join(basedir, largest_filename.replace('_' + bands[1], '_' + b)), b) for b in bands]
		filtered_largest_catalogs = [[subdirectory, c, b]\
									 for c, b in largest_catalogs if path.isfile(c)]
		add_to_copy_queue(filtered_largest_catalogs, dest_file)

