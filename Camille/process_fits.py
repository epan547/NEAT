"""
Made as part of research with Carrie Nugent
at Olin College of Engineering

Camille Xue 2019
Process Data from:
https://sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata/

Produce new folder with corrected fits images
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import lblparser
from astropy.io import fits


def process_image(image, dark, flat):
    """
    processes image:
        1. Subtract dark from flat
        2. Subtract dark from image
        3. Divide image by corrected flat
    """
    corrected_flat = flat - dark
    image_minus_dark = image - dark

    corrected_image = np.divide(image_minus_dark, corrected_flat)

    return np.array(corrected_image)


def get_image_names(image_folder):
    """
    Make array with all fits file names in given directory
    returns: array of filenames
    """
    names = []
    for filename in os.listdir(image_folder):
        filepath = image_folder + "/" + filename
        if filename.endswith(".fit.fz"):
            names.append(filename)
        if filename.endswith(".lbl"):
            image_lbl = lblparser.lbl_parse((filepath))
            # check fields to make sure they're correct
            if image_lbl["TARGET_NAME"] != "\"ASTEROID\"" or image_lbl["FILTER_NAME"] != "\"NONE\"":
                # remove fits file if not correct
                names.remove(filename.rstrip(".lbl")+".fit.fz")
                print(image_lbl["TARGET_NAME"])
                print(image_lbl["FILTER_NAME"])
                print("TARGET_NAME not ASTEROID || FILTER_NAME not NONE")
    return names

def get_image(images_folder, filename):
    """
    Gets image fits data
    images_folder: directory where image files located

    returns: matrix of data from fits file
    """
    filepath = images_folder + "/" + filename
    image_data = fits.getdata(filepath)
    return np.array(image_data)


def get_dark(darks_folder):
    """
    Gets dark fits data
    darks_folder: directory where dark files located

    Assumes there are two files in flats_folder
    <dark>.fit.fz and it's corresponding <dark>.lbl

    returns: matrix of data from fits file
    """
    for filename in os.listdir(darks_folder):
        filepath = darks_folder + "/" + filename
        if filename.endswith(".fit.fz"):
            dark_data = fits.getdata(filepath)
        # if filename.endswith(".lbl"):
        #     lbl_data = lblparser.lbl_parse(filepath)
    return np.array(dark_data)


def get_flat(flats_folder):
    """
    Gets flat fits data
    flats_folder: directory where flat files located

    Assumes there are two files in flats_folder
    <flat>.fit.fz and it's <flat>.lbl

    returns: matrix of data from flat fits file
    """
    for filename in os.listdir(flats_folder):
        filepath = flats_folder + "/" + filename
        if filename.endswith(".fit.fz"):
            flat_data = fits.getdata(filepath)
        if filename.endswith(".lbl"):
            lbl_data = lblparser.lbl_parse(filepath)
            if lbl_data["TARGET_NAME"] == "\"FLAT FIELD\"":
                # print("Flat Found")
                return flat_data
    return "Flat not found"

def make_fits(image_data, filename):
    hdu = fits.PrimaryHDU(image_data)
    if(os.path.isfile(filename)):
        print("Corrected file: \"{}\" already exists. \nOverwrite? [y/n]".format(filename))
        if(user_confirm()):
            os.remove(filename)
            hdu.writeto(filename)
        else:
            print("Corrected file not overwritten.")
    else:
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

    # directory names: "darks" "flats" "obsdata"
    dark = get_dark("darks") # fits data
    flat = get_flat("flats")
    image_names = get_image_names("obsdata")

    #

    # make directory where corrected images will go
    if not os.path.exists("corrected_obsdata"):
        os.mkdir("corrected_obsdata")

    # go through all the images in obsdata directory, process
    # them and make new files in new directory
    for image in image_names:
        image_data = get_image("obsdata", image)
        new_filename = "corrected_obsdata/corr_" + image
        processed_image = process_image(image_data, dark, flat)
        make_fits(processed_image, new_filename)

    # print(process_image(image_data, dark, flat))
