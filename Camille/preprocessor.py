"""
Made as part of research with Carrie Nugent
at Olin College of Engineering

Camille Xue 2019
Process Data from:
https://sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata/

HOW TO USE: have images in directory called "obsdata," darks in "darks," and
flats in "flats." There should be both the .lbl and .fit.fz files present.

FUNCTION: Produce new folder with corrected fits images

NOTE: Assumes darks and flats folders only have one dark and one flat in them,
currently doesn't have any methods for finding the correect flat/dark if given
multiple.

"""

import numpy as np
import matplotlib.pyplot as plt
import os
import lblparser
from astropy.io import fits
from astropy.nddata import CCDData

def all_data():
    """
    gets fits data and lbl dictionary for dark, flat, and obsdata.
    verifies lbl fields as given by list of requirements.

    returns: tuple (dark, flat, images) where dark and flat are dictionaries
    with "lbl" and "data" as keys.
    images is a dictionary of dictionaries with filenames as keys.
    """

    # flat
    flat = get_files("flats")
    flat_requirements = [("TARGET_NAME", "\"FLAT FIELD\"")]
    check_lbl_fields(flat["lbl"], flat_requirements)

    # dark
    dark = get_files("darks")
    dark_requirements = []
    check_lbl_fields(dark["lbl"], dark_requirements)

    # obsdata
    images = get_files("obsdata")
    image_requirements = [("TARGET_NAME", "\"ASTEROID\""), ("FILTER_NAME", "\"NONE\"")]
    for key in images.keys():
        check_lbl_fields(images[key]["lbl"], image_requirements)

    return (dark, flat, images)

def process_image(image, dark, flat):
    """
    given image, dark, and flat should be the fits data from fits.getdata()

    processes image:
        1. Subtract dark from flat
        2. Subtract dark from image
        3. Divide image by corrected flat

    returns: array of fits data but with corrected values
    """
    corrected_flat = flat - dark
    image_minus_dark = image - dark

    corrected_image = np.divide(image_minus_dark, corrected_flat)

    return np.array(corrected_image)


def get_files(directory: str) -> dict:
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
            print(filepath)
            files[name]["data"] = np.array(fits.getdata(filepath))

        elif ext == ".lbl":
            files[name]["lbl"] = lblparser.lbl_parse((filepath))
            # check_lbl_fields(filename, "obsdata")

    # for darks and flats there's only one file, so make one dictionary
    # instead of dictionary of nested dictionaries
    # obsdata image folder must have more than one image
    if directory != "obsdata":
        return files[name]

    # else:
    #     make_fits(files["960417070345a"]["data"], "original.fit.fz")
    return files

def check_lbl_fields(lbl: dict, requirements: list):
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
    hdul = fits.HDUList([hdu])
    if(os.path.isfile(filename)):
        print("Corrected file: \"{}\" already exists. \nOverwrite? [y/n]".format(filename))
        if(1):
            os.remove(filename)
            hdul.writeto(filename)
        else:
            print("Corrected file not overwritten.")
    else:
        print("Created file: {}".format(filename))
        hdul.writeto(filename)


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

    dark, flat, images = all_data()

    # make directory where corrected images will go
    if not os.path.exists("corrected_obsdata"):
        os.mkdir("corrected_obsdata")

    # process all the images
    for filename in images.keys():
        new_filename = "corrected_obsdata/corr_" + filename + ".fit.fz"
        image_data = images[filename]["data"]
        processed_image = process_image(image_data, dark["data"], flat["data"])
        make_fits(processed_image, new_filename)
