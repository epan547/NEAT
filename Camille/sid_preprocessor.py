from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.nddata import CCDData
from lblparser import lbl_parse
from datetime import datetime
import ccdproc
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

flats_folder_format = 'flats'
darks_folder_format = 'darks'
lights_folder_format = 'obsdata'

FMT = '%H:%M:%S'

geodss_data_volume = 'geodss/data'
tricam_data_volume = 'tricam/data'
tricam2_data_volume = 'tricam2/data'

sextractor_params = 'sexconf'
sextractor_output = 'sexout'
processed_volume = 'preprocessed'


def formFITSPaths(sample):
    """Use NEAT data conventions for mapping wget output locally to locations of files."""
    paths = dict()
    paths['darks'] = tricam_data_volume + \
        '/' + sample + '/' + darks_folder_format
    paths['flats'] = tricam_data_volume + \
        '/' + sample + '/' + flats_folder_format
    paths['lights'] = tricam_data_volume + \
        '/' + sample + '/' + lights_folder_format
    return paths


def findFITSFiles(sample):
    """Use paths to find all .fit samples and index samples accordingly."""
    paths = formFITSPaths(sample)
    files = dict()
    files['darks'] = glob.glob(paths['darks'] + '/*.fit')
    files['flats'] = glob.glob(paths['flats'] + '/*.fit')
    files['lights'] = glob.glob(paths['lights'] + '/*.fit')
    files['darks_lbl'] = glob.glob(paths['darks'] + '/*.lbl')
    files['flats_lbl'] = glob.glob(paths['flats'] + '/*.lbl')
    files['lights_lbl'] = glob.glob(paths['lights'] + '/*.lbl')
    return files


def odf_mapper(FITSFiles, light_idx):
    """Transforms light index into closest dark and flat indexes"""
    lab = lbl_parse(FITSFiles['lights'][light_idx][:-3]+"lbl")
    ttd = lab["START_TIME"].partition('T')

    best_didx = 0
    best_fidx = 0
    min_t_d_delta = 99999999
    min_t_f_delta = 99999999

    for didx in range(len(FITSFiles['darks'])):
        dta = lbl_parse(FITSFiles['darks'][didx][:-3]+"lbl")
        ttd_dta = dta["STOP_TIME"].partition('T')
        if ttd_dta[0] == ttd[0]:
            tdelta = abs((datetime.strptime(ttd_dta[2], FMT) - datetime.strptime(ttd[2], FMT)).total_seconds())
            if tdelta < min_t_d_delta:
                min_t_d_delta = tdelta
                best_didx = didx

    for fidx in range(len(FITSFiles['flats'])):
        fta = lbl_parse(FITSFiles['flats'][fidx][:-3]+"lbl")
        ttf_fta = fta["STOP_TIME"].partition('T')
        if (ttf_fta[0] == ttd[0]):
            tdelta = abs((datetime.strptime(ttf_fta[2], FMT) - datetime.strptime(ttd[2], FMT)).total_seconds())
            if tdelta < min_t_f_delta:
                min_t_f_delta = tdelta
                best_fidx = fidx

    light_lbl = lbl_parse(FITSFiles['lights'][light_idx][:-3]+"lbl")
    dark_lbl = lbl_parse(FITSFiles['darks'][best_didx][:-3]+"lbl")
    flat_lbl = lbl_parse(FITSFiles['flats'][best_fidx][:-3]+"lbl")

    if (flat_lbl['TARGET_NAME'] == '"FLAT FIELD"' and
            dark_lbl['TARGET_NAME'] == '"DARK"' and
            float(flat_lbl['EXPOSURE_DURATION'].partition('<')[0]) == float(dark_lbl['EXPOSURE_DURATION'].partition('<')[0]) and
            light_lbl['TARGET_NAME'] == '"ASTEROID"' and
            light_lbl['FILTER_NAME'] == '"NONE"' and
            float(light_lbl['EXPOSURE_DURATION'].partition('<')[0]) == float(dark_lbl['EXPOSURE_DURATION'].partition('<')[0])):
        return (best_didx,best_fidx,min_t_d_delta,min_t_f_delta)
    else:
        return (-1, -1, 0, 0)

def preprocessSampleData(light_idx, FITSFiles, longid):
    """Use provided correction methods to subtract out dark images and use flats to correct for vignetting.
       Write the processed file to the temporary preprocessed directory.
    """
    dark_idx, flat_idx, ttd, ttf = odf_mapper(FITSFiles, light_idx)
    print(ttd, ttf)

    if dark_idx < 0 and flat_idx < 0:
        print("NON-COMPLIANT")
        return;

    lights_lbl = lbl_parse(FITSFiles['lights_lbl'][light_idx])

    light = CCDData.read(FITSFiles['lights'][light_idx], unit='adu')
    dark = CCDData.read(FITSFiles['darks'][dark_idx], unit='adu')
    flat = CCDData.read(FITSFiles['flats'][flat_idx], unit='adu')

    corr = flat.data - dark.data
    corr1 = light.data - dark.data
    light.data = corr1/corr
    flat_corrected = light

    path_plan = processed_volume + "/" + sample + "/"
    try:
        print("Attempting to build path...")
        os.makedirs(path_plan)
        print("Built!")
        print("Writing to file " + str(longid.split('.')[0]) + ".fits")
        flat_corrected.write(path_plan + str(longid.split('.')[0]) + '.fits')
    except Exception as e:
        print("Directory already exists. Writing to file " + str(longid.split('.')[0]) + ".fits")
        flat_corrected.write(path_plan + str(longid.split('.')[0]) + '.fits')
    return flat_corrected


def process(sample, idx, longid):
    preprocessSampleData(idx, findFITSFiles(sample), longid)

sample = ''
palomar = next(os.walk('tricam/data'))[1]

for s in palomar:
    sample = s
    y = [x for x in next(
            os.walk('tricam/data/' + s + '/obsdata'))[2] if x.endswith("fit")]
    for i in range(len(y)):
        try:
            print("Processing sample " + s + " #" + str(i) + "...")
            process(s, i, y[i])
            print("Done.")
        except Exception as e:
            print("Error processing. Either the file already exists, or the primary HDU is corrupted/unused.")
            pass
