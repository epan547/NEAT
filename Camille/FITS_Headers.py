"""
Made as part of research with Carrie Nugent
at Olin College of Engineering

Camille Xue 2019
Data from:
https://sbnarchive.psi.edu/pds3/neat/geodss/data/g19960417/obsdata/

FUNCTION: Convert fits image headers into text files

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

processed_volume = 'obsdata_headers'

def get_hdrs_from_dir(directory):
    directory_path = target_data_volume + "/" + directory
    file_path = directory_path + "/" + img_data_folder

    # make directory where header directories will go
    processed_dir_path = target_volume + "/" + processed_volume
    if not os.path.exists(processed_dir_path):
        os.mkdir(processed_dir_path)
        print("directory: {} created".format(processed_dir_path))

    # make sub directory of header text files
    sub_dir_path = target_volume + "/" + processed_volume + "/" + directory
    print(sub_dir_path)

    if not os.path.exists(sub_dir_path):
        os.mkdir(sub_dir_path)
        print("directory:{} created".format(sub_dir_path))

    for filename in os.listdir(file_path):
        full_path = file_path + "/" + filename
        name = filename.split('.')[0]
        ext = '.' +'.'.join(filename.split('.')[1:])

        new_file_path = sub_dir_path + "/" + name + "_header.txt"

        if ext == ".fit.fz" or ext == ".fit":
            with fits.open(full_path) as hdul:
                print("Getting header: {}".format(filename))
                header = repr(hdul[1].header)
                with open(new_file_path, "w+") as new:
                    new.write(header)


if __name__ == "__main__":

    target_data_volume = target_volume + "/data"


    data_volume = next(os.walk(target_data_volume))
    for dir in os.listdir(target_data_volume):
            print("Processing directory: " + dir)
            get_hdrs_from_dir(dir)
            print("Done.")
