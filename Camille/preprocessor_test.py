import preprocessor as pf
import numpy as np
import matplotlib.pyplot as plt
import os
import lblparser
from astropy.io import fits

np.seterr(divide='ignore')

def process_image_test(image, dark, flat):
    """
    given image, dark, and flat should be the fits data from fits.getdata()

    processes image:
        1. Subtract dark from flat
        2. Subtract dark from image
        3. Divide image by corrected flat

    returns: array of fits data but with corrected values
    """
    # pf.make_fits(np.array(dark), "test/dark1.fit.fz")
    pf.make_fits(np.array(image), "test/original1.fit.fz")
    pf.make_fits(flat, "test/flat1.fit.fz")
    corrected_flat = flat - dark
    pf.make_fits(np.array(corrected_flat), "test/corrected_flat.fit.fz")

    image_minus_dark = image - dark
    pf.make_fits(np.array(image_minus_dark), "test/img_minus_dark.fit.fz")

    corrected_image = image_minus_dark / corrected_flat
    pf.make_fits(np.array(corrected_image), "test/final_processed.fit.fz")
    return corrected_image

if __name__ == "__main__":
    dark, flat, images = pf.all_data()
    # make directory where corrected images will go
    if not os.path.exists("test"):
        os.mkdir("test")
    # process all the images
    for filename in images.keys():
        new_filename = "corrected_obsdata/corr_" + filename
        image_data = images[filename]["data"]
        processed_image = process_image_test(image_data, dark["data"], flat["data"])
        # make_fits(processed_image, new_filename)
