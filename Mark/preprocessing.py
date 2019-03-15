from lblparser import lbl_parse
import ccdproc
import os


def preprocess(data_path):

	# Establish paths
	darks_path = './sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/darks'
	flats_path = './sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/flats'

	obsdata = create_data_dictionary(data_path)
	darks = create_data_dictionary(darks_path)
	flats = create_data_dictionary(flats_path)

def create_data_dictionary(data_path):

	""" Takes a list of .fit files and .lbl files and outputs a
		a dictionary with the .lbl files as keys and the corresponding
		.lbl files as values.

		data_path: file path to directory with .fit and .lbl files

		returns: dictionary with .lbl files as keys and corresponding .fit files as values
	"""

	# Check if the directory name is appropriate
	directoryName = data_path.split('/')[-1]
	if directoryName != 'flats' and directoryName != 'darks' and directoryName != 'obsdata':
		raise Exception('Cannot parse this directory. Directory name must be "obsdata", "darks", or "flats"')

	obsdata = dict()

	# Generates list of files in directory of the data_path
	for filename in os.walk(data_path):
		file_names = filename[2]


	for file in file_names:

		# Split file name from type
		fsplit = file.split('.')

		# Check if file is an asteroid image
		if fsplit[-1] == 'fz' or fsplit[-1] == 'fit':

			# Search list for matching .lbl file
			for file_search in file_names:

				fsplit_search = file_search.split('.')

				if fsplit_search[0] == fsplit[0] and fsplit_search[1] == 'lbl':

					# Add matching .lbl file as a key to the image in a dictionary
					obsdata[file_search] = file
			
	return obsdata




if __name__ == "__main__":
	res = preprocess('./sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata')
	print(res)