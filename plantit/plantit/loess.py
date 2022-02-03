import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm

from plantit.utils.misc import rescale, jitter


def get_band(distances: np.ndarray, width: int) -> np.ndarray:
    """
    Gets the indices of the band of the given width around

    :param distances: The array of distances from the current point to all other points
    :param width: The band width
    :return: The band indices
    """
    min_i = np.argmin(distances)
    total = len(distances)
    band = [min_i]

    # if the closest neighbor is at either the left or right bound, start the window there
    if min_i == 0: return np.arange(0, width)
    if min_i == total-1: return np.arange(total - width, total)

    # otherwise build it up iteratively
    while len(band) < width:
        min_i = band[0]
        max_i = band[-1]
        if min_i == 0: band.append(max_i + 1)
        elif max_i == total - 1: band.insert(0, min_i - 1)
        elif distances[min_i - 1] < distances[max_i + 1]: band.insert(0, min_i - 1)
        else: band.append(max_i + 1)

    return np.array(band)


def get_weights(distances: np.ndarray, band: np.ndarray) -> np.ndarray:
    """
    Calculates weights of neighboring (band) points

    :param distances: The array of distances from the current point to all other points
    :param band: The array of indices of the band (neighboring points)
    :return: The weights of the band points
    """

    normed_ds = distances[band] / np.max(distances[band])
    bandwidth = len(band)
    mu = 0
    sd = bandwidth * np.std(normed_ds)
    x = np.linspace(mu - sd, mu + sd, len(normed_ds))
    weights = stats.norm.pdf(x, mu, sd)
    # weights = normal_weights(normed_ds, len(band))
    # weights = tricubic_weights(normed_distances

    return weights


def regress(data: pd.DataFrame, bandwidth: int, num_pts: int) -> pd.DataFrame:
    """
    Performs LOESS regression.

    :param data: The data frame or matrix, with the predictor in the first column and the response in the second
    :param bandwidth: The bandwidth (lambda)
    :param num_pts: The number of points to predict over
    :return: The output matrix, with x values in the first column and predictions in the second
    """

    # extract the predictor and response and compute their respective min and max values
    xs = data.iloc[:,0]
    x_min = np.min(xs)
    x_max = np.max(xs)

    # extract the response
    ys = data.iloc[:,1]
    y_min = np.min(ys)
    y_max = np.max(ys)

    # scale the predictor and response to unit interval
    normed_xs = np.interp(xs, (x_min, x_max), (0, 1))
    normed_ys = np.interp(ys, (y_min, y_max), (0, 1))

    print(pd.DataFrame({'X': normed_xs, 'Y': normed_ys}))

    # predict n evenly spaced points over the output range
    output_xs = np.linspace(x_min, x_max, num_pts)
    output_ys = []

    for x in output_xs:
        # rescale the value to the unit interval
        normed_x = rescale(x, x_min, x_max)

        # compute distances from this value to all other values
        distances = np.abs(normed_xs - normed_x)

        # get the indices of the band around the current points
        band_is = get_band(distances, bandwidth)

        # get weights for elements of the band
        weights = get_weights(distances, band_is)

        # get the subsets of the normed predictor and response corresponding to the band
        band_xs = normed_xs[band_is]
        band_ys = normed_ys[band_is]

        # print(pd.DataFrame({'X': band_xs, 'Y': band_ys}))

        # fit weighted least squares model to the band
        wls = sm.WLS(band_ys, band_xs, weights=weights)
        wls_results = wls.fit()
        wls_y = wls_results.predict(normed_x)

        output_ys.append(wls_y)

    # rescale the response to the original interval
    output_ys = [y for yy in np.interp(output_ys, (0, 1), (y_min, y_max)) for y in yy]
    return pd.DataFrame({'X': output_xs, 'Y': output_ys})
