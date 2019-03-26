import sewpy
sew = sewpy.SEW(params=["X_IMAGE", "Y_IMAGE", "FLUX_RADIUS(3)", "FLAGS"],
        config={"DETECT_MINAREA":10, "PHOT_FLUXFRAC":"0.3, 0.5, 0.8"})
out = sew("myimage.fits")
print out["table"] # this is an astropy table.
