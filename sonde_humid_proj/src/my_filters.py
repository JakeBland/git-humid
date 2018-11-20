"""
Collection of functions to smooth arrays and cubes with filters
"""

from __future__ import division

from scipy.signal import savgol_filter
import numpy as np

import random
import matplotlib.pyplot as plt
#import Sophie_code.write_all_regions as swar


def filter_cubelist(cubelist_original, filter_dic):
    """
    Apply chosen filter to data in all cubes in CubeList
    :param cubelist_original: list of cubes whose data are to be filtered
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :return: CubeList of cubes with smoothed data fields
    """

    cubelist = cubelist_original
#    cubelist = cubelist_original.copy()

    for cube in cubelist:
        
        if cube.shape == (1,) or cube.shape == ():
            # these cubes do not have dimension
            pass
        else:            
            cube.data = my_filter(cube.data, filter_dic)

    return cubelist

def my_filter(array, filter_dic):
    """
    Filters data to smooth out noise
    :param array: data array to be smoothed
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :return: smoothed array
    """

    if filter_dic['name'] == 'savgol':

        return savgol_filter(array, filter_dic['window'], filter_dic['order'])

    elif filter_dic['name'] == 'kernel':

        return kernel_filter(array, filter_dic['gaussian_half_width'])

    else:

        print 'No filter'
        return array


def kernel_filter(array, d):
    """
    Calls filter taken from Sophie code and modified
    :param array: data array to be smoothed
    :param d: gaussian half width == 1/4 window size
    :return: smoothed array
    """
    return smooth_equal_intervals(array, d)


def tenm_weights(d):
    # taken from sophie and modified to use array arithmetic instead of for loops
    # Calculates weights for a truncated gaussian smoothing with half-width d and points every 10m
    # d is gaussian half width in meters
    # window size is defined as being four times the half-width of the gaussian - i.e. 2d either side of point
    #:return: array of normalised weights (len 0.2*d + 1)

    weights = [np.exp(-((10 * i) ** 2) / (2 * d ** 2)) for i in range(0, int(0.2 * d + 1))]
    # create half a weighting curve
    weights = np.array(weights[-1:0:-1] + weights)
    # append because they are lists, then turn into an array
    return weights/sum(weights)


def smooth_equal_intervals(array, d):
    # taken from sophie and modified to use array arithmetic instead of for loops
    # Smooth an array using a truncated Gaussian assuming points are spaced 10m appart
    # d is gaussian half width in meters
    # two half widths are considered either side of a point when calculating smoothing on it
    #:return: filtered array

    weights = tenm_weights(d)
    new_arr = []
    lena = len(array)

    for i in range(lena):

        hw = int(0.2 * d)
        # half width in grid boxes, assuming 10m grid = 2 * d, two half widths of the gaussian (CONFUSING TERMINOLOGY)

        if i < hw or i >= lena - hw:

            i2 = min(i, lena - i - 1)
            # shortest distance to an end point = minimum half-width of a kernel to use
            newweights = weights[hw - i2 : hw + i2 + 1]
            # ensures window is symmetric, so as not to take more information from one side or the other
            newweights = newweights/sum(newweights)
            # re-normalise
            hw = i2
            # new half-width
            
        else:
            
            newweights = weights
        
        new_arr.append(sum(array[i - hw : i + hw + 1] * newweights))

    return np.array(new_arr)

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

def test_filter():
    # tests filters using sinusoid with added noise
    
    kernel_dic = {'name' : 'kernel', 'gaussian_half_width' : 50} 
    
    savgol_dic = {'name' : 'savgol', 'window' : 21, 'order' : 3}
    
    x = np.array(range(100)) # equivalent of 1km in 10m intervals
    
    ys = 10*np.sin(x/5)
    
    y = ys.copy()
    
    for n in x:
        y[n] += random.randint(1, 201)/100 - 1
    
    yk = my_filter(y, kernel_dic)
    
    yg = my_filter(y, savgol_dic)
    
    plt.figure(figsize = (12, 8))
    plt.plot(ys, label = 'original')
    plt.plot(y, label = 'noisy')
    plt.plot(yk, label = 'kernel_smooth')
    plt.plot(yg, label = 'Savitsky-Golay')
    plt.legend()
    plt.title('Profile smoothing using window of 21 points (for kernel, gaussian half-width = 5 points, 2 half widths either side)')
    plt.show()
    
    xk = my_filter(x, kernel_dic)
    xg = my_filter(x, savgol_dic)
    
    plt.figure(figsize = (12, 8))
    plt.plot(x, label = 'original')
    plt.plot(xk, label = 'kernel_smooth')
    plt.plot(xg, label = 'Savitsky-Golay')
    plt.legend()
    plt.show()
    
    