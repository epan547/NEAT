# from astropy.utils.data import download_file
from astropy.io import fits
import numpy as np
# Set up matplotlib and use a nicer set of plot parameters
# %config InlineBackend.rc = {}
import matplotlib
# matplotlib.rc_file("../../templates/matplotlibrc")
import matplotlib.pyplot as plt
# %matplotlib inline

# image_file = download_file('http://data.astropy.org/tutorials/FITS-images/HorseHead.fits', cache=True )

# hdu_list = fits.open(image_file)
# image_data = hdu_list[0].data
# hdu_list.close()

image_data = fits.getdata('96_04_17a_20secnrm_flat.fit.fz')

plt.figure(1)
plt.imshow(image_data, cmap='gray')
plt.colorbar()
plt.show()
