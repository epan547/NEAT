import sewpy
import ccdproc
sew = sewpy.SEW(params=["X_IMAGE", "Y_IMAGE", "FLUX_RADIUS(3)", "FLAGS"],
        config={"DETECT_MINAREA":10, "PHOT_FLUXFRAC":"0.3, 0.5, 0.8"})
out = sew("96_04_17a_20secnrm_flat.fit")
# print(out["table"]) # this is an astropy table.
print(out)
