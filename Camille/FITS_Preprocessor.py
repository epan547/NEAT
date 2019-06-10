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

overwrite_ok = 1 # automatically overwrite without asking permission

flats_folder = 'flats'
darks_folder = 'darks'
img_data_folder = 'obsdata'

geodss_data_volume = 'geodss'
tricam_data_volume = 'tricam'
tricam2_data_volume = 'tricam2'

# change this to choose which to process: geodss, tricam, tricam2, etc
target_volume = geodss_data_volume

processed_volume = 'obsdata_reduction'
FMT = '%H:%M:%S'

def process_directory(directory):
    """
    Processes all darks, flats, and image data in given directory.
    i.e. geodss, tricam, tricam2

    Creates new directory with processed_volume as name, creates
    sub directories to match hierarchy of /data folder
    """
    directory_path = target_data_volume + "/" + directory
    darks, flats, images = all_files(directory_path)

    # make directory where corrected directories will go
    processed_dir_path = target_volume + "/" + processed_volume
    if not os.path.exists(processed_dir_path):
        os.mkdir(processed_dir_path)
        print("directory: {} created".format(processed_dir_path))

    # make sub directory of corrected images
    sub_dir_path = target_volume + "/" + processed_volume + "/" + directory
    print(sub_dir_path)
    if not os.path.exists(sub_dir_path):
        os.mkdir(sub_dir_path)
        print("directory:{} created".format(sub_dir_path))

    new_file_path = sub_dir_path + "/"

    # process all the images
    for filename in images.keys():
        print("Processing: {}".format(filename))
        new_filename = new_file_path + filename + "_R.fit"
        dark_data, flat_data = match_dark_flat(images[filename]["lbl"], darks, flats)
        processed_image = process_image(images[filename], dark_data, flat_data)
        make_fits(processed_image, new_filename)

def all_files(directory):
    """
    gets fits data and lbl dictionary for dark, flat, and obsdata.
    verifies lbl fields as given by list of requirements.

    returns: tuple (dark, flat, images) where dark, flat, and
    images are dictionaries of dictionaries with filenames as keys.
    """

    # flat
    flat = get_dir_files(directory + "/"+ flats_folder)
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

def get_dir_files(directory):
    """
    Make dictionary of filenames in given directory
    files["filename"]["data"] = fits data
    files["filename"]["lbl"] = lbl info
    files["filename"]["header"] = fits header info

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
            with fits.open(filepath) as hdul:
                files[name]["data"] = hdul[1].data
                files[name]["header"] = hdul[1].header

        elif ext == ".lbl":
            files[name]["lbl"] = lblparser.lbl_parse((filepath))

    # check for files missing their fit or lbl
    missing = [name for name in files.keys() if len(files[name]) != 3]
    for m in missing:
        print("Missing corresponding fits or lbl for file: " + m)
        del files[m]

    return files # nested dictionary -> files[filename][lbl or data]

def match_dark_flat(image_lbl, darks, flats):
    """
    Picks the closest dark/flat based on time for the
    given image.

    returns: selected dark & flat data
    """
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

def check_lbl_fields(lbl, requirements):
    for r in requirements:
        if lbl[r[0]] != r[1]:
            print("Error in file: {}".format(lbl["^HEADER"]))
            raise Exception("Invalid value for lbl field {}. Expected {} not {}".format(r[0], r[1], lbl[r[0]]))

def process_image(image, dark, flat):
    """
    image is image dict with data & header preserved
    dark & flat only need the ["data"]

    processes image:
        1. Subtract dark from image
        2. Divide by flat
        NOTE: flats from NEAT are already corrected

    returns: dictionary of header & fits data but with corrected values
    """
    corrected_image = {}
    corrected_image["header"] = image["header"]

    image_minus_dark = image["data"] - dark
    corrected_image["data"] =  image_minus_dark / flat

    return corrected_image

def make_fits(image, filename):
    """
    Creates fits file with given data and filename
    if the filename exists, it will confirm with user if it should be
    overwritten.
    """
    hdu = fits.CompImageHDU(image["data"], header=image["header"])

    if(os.path.isfile(filename)): # file already exists
        if(overwrite_ok):
            os.remove(filename)
            hdu.writeto(filename)
            # print("File Overwritten: {}".format(filename))
        else:
            print("Corrected file: \"{}\" already exists. \nOverwrite? [y/n]".format(filename))
            if(user_confirm()):
                os.remove(filename)
                hdu.writeto(filename)
                print("File Overwritten: {}".format(filename))
            else:
                print("Corrected file not overwritten.")
                pass
    else:
        print("Created file: {}".format(filename))
        hdu.writeto(filename)

def user_confirm():
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

    target_data_volume = target_volume + "/data"

    data_volume = next(os.walk(target_data_volume))
    for dir in os.listdir(target_data_volume):

        try:
            print("Processing directory: " + dir)
            process_directory(dir)
            print("Done.")
        except Exception as e:
            print("Error Processing in Directory: " + dir)
            print(e)
            pass
