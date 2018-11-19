from __future__ import division

from scipy.signal import savgol_filter
import numpy as np

def my_filter(array, filter_dic):

    if filter_dic['name'] = 'savgol':

        return savgol_filter(array, filter_dic['window']*2 +1, filter_dic['order'])

    elif filter_dic['name'] = 'kernel':

        return kernel_filter(array, filter_dic['window'], filter_dic['d'])

    else

        print 'No filter'
        return array


def kernel_filter(array, d):
    
    return smooth_equal_10m_intervals(array, d)


def tenm_weights(d):
    # taken from sophie and modified to use array arithmetic instead of for loops
    # Calculates weights for a truncated gaussian smoothing with half-width d and points every 10m
    # d is gaussian half width in meters

    weights = [np.exp(-((10 * i) ** 2) / (2 * d ** 2)) for i in range(0, int(0.2 * d + 1))]
    # create half a weighting curve
    weights = np.array(weights[-1:0:-1] + weights)
    # append because they are lists, then turn into an array
    return weights/sum(weights)


def smooth_equal_10m_intervals(array, d):
    # taken from sophie and modified to use array arithmetic instead of for loops
    # Smooth an array using a truncated Gaussian assuming points are spaced 10m appart
    # d is gaussian half width in meters
    # two half widths are considered either side of a point when calculating smoothing on it

    weights = tenm_weights(d)
    new_arr = []
    lena = len(array)

    for i in range(lena):

        hw = int(0.2 * d)
        # half width in grid boxes, assuming 10m grid = 2 * d, two half widths of the gaussian (CONFUSING TERMINOLOGY)

        if i < hw or i >= lena - hw:

            i2 = min(i, lena - i - 1)
            # shortest distance to an end point = minimum half-width of a kernel to use
            weights = weights[hw - i2 : hw + i2 + 1]
            # ensures window is symmetric, so as not to take more information from one side or the other
            weights = weights/sum(weights)
            # re-normalise
            hw = i2
            # new half-width

        new_arr.append(sum(array[i - hw : i + hw + 1] * weights[j]))

    return new_arr

# sophie's original stuff
#    for i in range(len(Theta)):
#        if i >= int(200 * d) and i < len(Theta) - int(200 * d):
#            weightedvalues = [Theta[i - int(200 * d) + j] * weights[j] for j in range(len(weights))]
#            newTheta += [sum(weightedvalues)]
#        else:
#            newweights = weights
#            if i >= len(Theta) - int(200 * d):
#                newweights = newweights[:int(200 * d) + len(Theta) - i]
#            if i < int(200 * d):
#                newweights = newweights[int(200 * d) - i:]
#            total = sum(newweights)
#            newweights = [x / total for x in newweights]
#            if i < int(200 * d):
#                weightedvalues = [Theta[j] * newweights[j] for j in range(len(newweights))]
#            else:
#                weightedvalues = [Theta[i - int(200 * d) + j] * newweights[j] for j in range(len(newweights))]
#            newTheta += [sum(weightedvalues)]
#    return newTheta