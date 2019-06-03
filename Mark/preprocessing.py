from lblparser import lbl_parse
from astropy import units as u
from astropy.io import fits
from astropy.io.fits import getdata
from astropy.nddata import CCDData 
import ccdproc
import os

class Preprocessor(object):

	"""
		This class is to preprocess images from the NEAT dataset by
		accounting for darks and flats

	"""

	def __init__(self, data_path, darks_path, flats_path):


		# Establish paths
		self.data_path = data_path
		self.darks_path = darks_path
		self.flats_path = flats_path


	def preprocess(self):


		# create dictionary of file names where the key is a .lbl and the value is a .fit
		obsdata = self.create_data_dictionary(self.data_path)
		darks = self.create_data_dictionary(self.darks_path)
		flats = self.create_data_dictionary(self.flats_path)

		# List to populate which allow for the comparison of exposure times for darks and flats
		dark_exposures = list()
		flat_exposures = list()

		# Check that everything in the darks/flats directories are darks/flats and make lists of exposure times
		for dark in darks.keys():
			assert (self.target_name_check(dark, 'DARK')), dark + " is not labeled as a Dark!"
			dark_exposures.append(lbl_parse(self.darks_path + '/' + dark)['EXPOSURE_DURATION'])
		for flat in flats.keys():
			assert (self.target_name_check(flat, 'FLAT FIELD')), flat + " is not labeled as a Flat!"
			flat_exposures.append(lbl_parse(self.flats_path + '/' + flat)['EXPOSURE_DURATION'])


		# Make sure that the lists of exposure times are identical
		assert (dark_exposures == flat_exposures), "Flats and darks do not have the same exposure times!"

		# Check that each asteroid is labeled as asteroid and preprocess them
		for image in obsdata.keys():
			assert (self.target_name_check(image, 'ASTEROID')), image + " is not labeled as an Asteroid or the filter type is not NONE!"

		# Correct the flat
		corrected_flats = list()
		for dark, flat in zip(darks.values(),flats.values()):
			corrected_flats.append(self.flat_corrector(dark,flat))


		# For each image correct the image itself and then divide by the corrected flat
		preprocessed_images = list()
		for image in obsdata.values():
			preprocessed_images.append(self.image_corrector(image, dark, corrected_flats[0]))


		return preprocessed_images



	def image_corrector(self, image, dark, corrected_flat):


		""" 
			Subtracts the dark from the original image, producing a corrected image. 
			This corrected image is then element-wise divided by the corrected flat.

			returns: final corrected image 
		"""

		image_object = CCDData(getdata(self.data_path + '/' + image), unit='adu')
		dark_object = CCDData(getdata(self.darks_path + '/' + dark), unit='adu')

		corrected_image_1 = CCDData.subtract(image_object,dark_object)

		corrected_image_final = CCDData.divide(corrected_image_1,corrected_flat)

		return corrected_image_final


	def flat_corrector(self, dark, flat):


		""" 
			Subtracts the dark from the flat producing the corrected flat.

			returns: corrected flat
		"""

		flat_object = CCDData(getdata(self.flats_path + '/' + flat), unit='adu')
		dark_object = CCDData(getdata(self.darks_path + '/' + dark), unit='adu')

		correct = CCDData.subtract(flat_object,dark_object)

		return CCDData(correct, unit='adu')

	def target_name_check(self, image, type):

		"""
			Checks if .lbl file contains TARGET_NAME = type

			returns: True if TARGET_NAME is user-inputted type and false otherwise
		"""

		# Get correct file path based off of type
		if type == 'DARK':
			path = self.darks_path
			return lbl_parse(path + '/' + image)['TARGET_NAME'] == "\"" + type + "\""
		elif type == 'FLAT FIELD':
			path = self.flats_path
			return lbl_parse(path + '/' + image)['TARGET_NAME'] == "\"" + type + "\""
		else:
			path = self.data_path
			return lbl_parse(path + '/' + image)['TARGET_NAME'] == "\"" + type + "\"" and lbl_parse(path + '/' + image)['FILTER_NAME'] == "\"NONE\""

	def create_data_dictionary(self, data_path):

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
	p = Preprocessor('./sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata','./sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/darks','./sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/flats')
	res = p.preprocess()
	print(res)