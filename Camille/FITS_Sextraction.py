from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.nddata import CCDData
import ccdproc
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

geodss_data_volume = 'geodss'
tricam_data_volume = 'tricam'
tricam2_data_volume = 'tricam2'

sextractor_params = 'sexconf'
sextractor_output = 'sexout'
processed_volume = 'obsdata_reduction'

# change this to source extract different data
target_volume = geodss_data_volume

sample = ''
proc = next(os.walk(processed_volume))[1]
sample_path = target_volume + "/" + processed_volume + "/"

for dir in os.listdir(sample_path):
    dir_path = sample_path + "/" + dir + "/"
    for file in os.listdir(dir_path):
        base_name = dir + '-' + file[:-12]
        print("Analyzing: {} - {}".format(dir,file))
        # cd sexconf && sox ../filepath [various parameters]
        os.system( "cd " + sextractor_params +
        " && sex ../" + dir_path + file +
        " -PARAMETERS_NAME sex_outcols.txt -STARNNW_NAME default_nnw.txt -c wisesex_params.txt -WEIGHT_GAIN N,N -CATALOG_NAME " +
        base_name + "-sex-cat.txt -DEBLEND_NTHRESH 32 -DEBLEND_MINCONT 0.0001 -BACK_SIZE 130")
        # outputs catalog text file

        # TODO: move file to its own directory in sexout

        # move check image to sexout folder
        os.system("cd " + sextractor_params + " && mv check.fits ../" + sextractor_output + "/" + base_name + "_check.fits")

# move output to sexout folder
os.system("cd " + sextractor_params + " && mv *-cat.txt ../" + sextractor_output)
os.system("cd " + sextractor_params + " && mv *.fits ../" + sextractor_output)

print("Finished. Catalog created at " + sextractor_output + " folder.")
print("---------------------")
