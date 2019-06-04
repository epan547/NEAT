"""
Made as part of research with Carrie Nugent
at Olin College of Engineering

Camille Xue 2019
Process Data from:
https://sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata/

FUNCTION: Produce new folder with corrected fits images

"""

import numpy as np
import matplotlib.pyplot as plt
import os
import lblparser
from datetime import datetime
from astropy.io import fits
from astropy.nddata import CCDData

flats_folder = 'flats'
darks_folder = 'darks'
img_data_folder = 'obsdata'

geodss_data_volume = 'geodss/data'
tricam_data_volume = 'tricam/data'
tricam2_data_volume = 'tricam2/data'

processed_volume = 'obsdata_reduction'
FMT = '%H:%M:%S'


def all_files(directory):
    """
    gets fits data and lbl dictionary for dark, flat, and obsdata.
    verifies lbl fields as given by list of requirements.

    returns: tuple (dark, flat, images) where dark and flat are dictionaries
    with "lbl" and "data" as keys.
    images is a dictionary of dictionaries with filenames as keys.
    """

    # flat
    flat = get_dir_files(directory +"/"+ flats_folder)
    flat_requirements = [("TARGET_NAME", "\"FLAT FIELD\"")]
    for key in flat.keys():
        check_lbl_fields(flat[key]["lbl"], flat_requirements)

    # dark
    dark = get_dir_files(directory +"/"+ darks_folder)
    dark_requirements = []

    # obsdata
    images = get_dir_files(directory +"/"+ img_data_folder)
    image_requirements = [("TARGET_NAME", "\"ASTEROID\""), ("FILTER_NAME", "\"NONE\"")]
    for key in images.keys():
        check_lbl_fields(images[key]["lbl"], image_requirements)

    return (dark, flat, images)

def process_image(image, dark, flat):
    """
    given image, dark, and flat should be the fits data from fits.getdata()

    processes image:
        1. Subtract dark from image
        2. Divide by flat

    returns: array of fits data but with corrected values
    """
    image_minus_dark = image - dark

    corrected_image =  image_minus_dark / flat

    return corrected_image


def get_dir_files(directory):
    """
    Make dictionary of filenames in given directory
    files["filename"]["data"] = fits data
    files["filename"]["lbl"] = lbl info

    returns: dictionary of files
    """
    files = {}
    for filename in os.listdir(directory):
        filepath = directory + "/" + filename
        name = filename.split('.')[0]
        ext = '.' +'.'.join(filename.split('.')[1:])

        if name not in files:
            files[name] = {}

        if ext == ".fit.fz" or ext == ".fit":
            files[name]["data"] = np.array(fits.getdata(filepath))

        elif ext == ".lbl":
            files[name]["lbl"] = lblparser.lbl_parse((filepath))
            # check_lbl_fields(filename, "obsdata")

    return files # nested dictionary -> files[filename][lbl or data]

def check_lbl_fields(lbl, requirements):
    for r in requirements:
        if lbl[r[0]] != r[1]:
            raise Exception("Invalid value for lbl field {}. Expected {} not {}".format(r[0], r[1], lbl[r[0]]))


def make_fits(image_data, filename):
    """
    Creates fits file with given data and filename
    if the filename exists, it will confirm with user if it should be
    overwritten.
    """
    hdu = fits.PrimaryHDU(image_data)

    if(os.path.isfile(filename)):
        print("Corrected file: \"{}\" already exists. \nOverwrite? [y/n]".format(filename))
        if(user_confirm()):
            os.remove(filename)
            hdu.writeto(filename)
            print("File Overwritten: {}".format(filename))
        else:
            print("Corrected file not overwritten.")
    else:
        print("Created file: {}".format(filename))
        hdu.writeto(filename)

def match_dark_flat(image_lbl, darks, flats):
    img_datetime = image_lbl["START_TIME"].partition('T')

    min_t_diff_dark = 9999999
    min_t_diff_flat = 9999999

    for dark in darks.keys():
        dark_datetime = darks[dark]["lbl"]["STOP_TIME"].partition('T')
        if dark_datetime[0] == img_datetime[0]: # same day
            diff = abs((datetime.strptime(dark_datetime[2], FMT) - datetime.strptime(img_datetime[2], FMT)).total_seconds())
            if diff < min_t_diff_dark:
                min_t_diff_dark = diff
                match_dark = dark


    for flat in flats.keys():
        flat_datetime = flats[flat]["lbl"]["STOP_TIME"].partition('T')
        if flat_datetime[0] == img_datetime[0]: # same day
            diff = abs((datetime.strptime(flat_datetime[2], FMT) - datetime.strptime(img_datetime[2], FMT)).total_seconds())
            if diff < min_t_diff_flat:
                min_t_diff_flat = diff
                match_flat = flat

    return darks[match_dark]["data"], flats[match_flat]["data"]

def process_directory(directory):
    darks, flats, images = all_files(directory)
    # make directory where corrected images will go
    if not os.path.exists(directory + "/" + processed_volume):
        os.mkdir(directory + "/" +processed_volume)
    new_path = directory + "/" + processed_volume +"/"

    # process all the images
    for filename in images.keys():
        print("Processing: {}".format(filename))
        new_filename = new_path + filename + "_reduced.fit"
        image_data = images[filename]["data"]
        dark_data, flat_data = match_dark_flat(images[filename]["lbl"], darks, flats)
        processed_image = process_image(image_data, dark_data, flat_data)
        make_fits(processed_image, new_filename)

def user_confirm():
    return True # TODO: remove when done testing
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}
    choice = input().lower()
    if choice in yes:
       return True
    elif choice in no:
       return False
    else:
       print("Please respond with 'yes' or 'no'")


if __name__ == "__main__":

    process_directory("p20011122")
