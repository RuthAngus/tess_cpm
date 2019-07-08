import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.mast import Tesscut

def get_data(ra, dec, units="deg", size=64):
    c = SkyCoord(ra, dec, units=units)
    data_table = Tesscut.download_cutouts(c, size=size)
    return data_table

def plot_lightcurves(cpm):
    fig, axs = plt.subplots(2, 1, figsize=(18, 12))
    data = cpm.target_fluxes
    model = cpm.lsq_prediction
    res = data - cpm.cpm_prediction
    
    axs[0].plot(cpm.time, data, ".", color="k", label="Data", markersize=6)
    axs[0].plot(cpm.time, model, ".", color="C3", label="Model", markersize=4, alpha=0.6)
    if (cpm.poly_params.shape != (0,)):
        axs[0].plot(cpm.time, cpm.cpm_prediction, ".", color="C1", label="CPM", markersize=4, alpha=0.4)
        axs[0].plot(cpm.time, cpm.poly_prediction, "-", color="C2", label="Poly", markersize=4, alpha=0.7)
    
    axs[1].plot(cpm.time, res, ".-", label="Residual (Data - CPM)", markersize=3)

    for i in range(2):
        axs[i].legend(fontsize=15)
    plt.show()

def summary_plot(cpm, n, save=False):
    """Shows a summary plot of a CPM fit to a pixel.

    The top row consists of three images: (left) image showing median values for each pixel,
    (middle) same image but the target pixel (the pixel we are trying to predict the lightcurve for),
    the exclusion region (area where predictor pixels CANNOT be chosen from), and the predictor pixels are shown,
    (right) same image but now the top-``n`` contributing pixels of the CPM are shown. The contribution is 
    defined as the absolute value of the coefficients of each predictor pixel. For example, the top 5 contributing pixels
    are the pixels which have the highest absolute coefficient values calculated when ``lsq`` is run.   

    """
    top_n_loc, top_n_mask = cpm.get_contributing_pixels(n)
    
    plt.figure(figsize=(18, 14))
    
    ax1 = plt.subplot2grid((4, 3), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((4, 3), (0, 1), rowspan=2)
    ax3 = plt.subplot2grid((4, 3), (0, 2), rowspan=2)
    
    ax4 = plt.subplot2grid((4, 3), (2, 0), colspan=3)
    ax5 = plt.subplot2grid((4, 3), (3, 0), colspan=3)
    
    first_image = cpm.pixel_medians

#     first_image = cpm.im_fluxes[0,:,:]
    ax1.imshow(first_image, origin="lower",
           vmin=np.percentile(first_image, 10), vmax=np.percentile(first_image, 90))
    
    ax2.imshow(first_image, origin="lower",
           vmin=np.percentile(first_image, 10), vmax=np.percentile(first_image, 90))
    ax2.imshow(cpm.excluded_pixels_mask, origin="lower", cmap="Set1", alpha=0.5)
    ax2.imshow(cpm.target_pixel_mask, origin="lower", cmap="binary", alpha=1.0)
    ax2.imshow(cpm.predictor_pixels_mask, origin="lower", cmap="binary_r", alpha=0.9)
    
    ax3.imshow(first_image, origin="lower",
           vmin=np.percentile(first_image, 10), vmax=np.percentile(first_image, 90))
    ax3.imshow(cpm.excluded_pixels_mask, origin="lower", cmap="Set1", alpha=0.5)
    ax3.imshow(cpm.target_pixel_mask, origin="lower", cmap="binary", alpha=1.0)
    ax3.imshow(cpm.predictor_pixels_mask, origin="lower", cmap="binary_r", alpha=0.9)
    ax3.imshow(top_n_mask, origin="lower", cmap="Set1")
    
    data = cpm.target_fluxes
    model = cpm.lsq_prediction
#     res = data - model
    res = data - cpm.cpm_prediction
    
    ax4.plot(cpm.time, data, ".", color="k", label="Data", markersize=4)
    ax4.plot(cpm.time, model, ".", color="C3", label="Model", markersize=4, alpha=0.4)
    if (cpm.poly_params.shape != (0,)):
        ax4.plot(cpm.time, cpm.cpm_prediction, ".", color="C1", label="CPM", markersize=3, alpha=0.4)
        ax4.plot(cpm.time, cpm.poly_prediction, ".", color="C2", label="Poly", markersize=3, alpha=0.4)
    
#     ax5.plot(cpm.time, res, ".-", label="Residual (Data - Model)", markersize=7)
    if (cpm.poly_params.shape != (0,)):
        ax5.plot(cpm.time, res, ".-", label="Residual (Data - CPM)", markersize=7)
    else:
        ax5.plot(cpm.time, data - cpm.lsq_prediction, ".-", label="Residual (Data - Model)", markersize=7)
    
    plt.suptitle("N={} Predictor Pixels, Method: {}, L2Reg={}".format(cpm.num_predictor_pixels,
                cpm.method_predictor_pixels, "{:.0e}".format(cpm.regularization)), y=0.89, fontsize=15)
    
    ax1.set_title("Cmap set to 10%, 90% values of image")
    ax2.set_title("Target (White), Excluded (Red Shade), Predictors (Black)")
    ax3.set_title("Top N={} contributing pixels to prediction (Red)".format(n))
    
    ax4.set_title("Lightcurves of Target Pixel {}".format((cpm.target_row, cpm.target_col)))
    ax4.set_ylabel("Flux [e-/s]")
    ax4.legend(fontsize=12)
    
    ax5.set_xlabel("Time (BJD-2457000) [Day]", fontsize=12)
    ax5.set_ylabel("Flux [e-/s]")
    ax5.legend(fontsize=12)
    
    if (save == True):
        plt.savefig("cpm_target_{}_reg_{}_filename_{}.png".format((cpm.target_row,cpm.target_col),
                    "{:.0e}".format(cpm.regularization), cpm.file_name), dpi=200)

# def sap(row, col, size, diff):
#     """Simple Aperture Photometry for a given pixel.

#     """
#     aperture = diff[:, max(0, row-size):min(row+size+1, diff.shape[1]), 
#                     max(0, col-size):min(col+size+1, diff.shape[1])]
#     aperture_lc = np.sum(aperture, axis=(1, 2))
#     return aperture, aperture_lc
