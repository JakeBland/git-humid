"""
File of conditions which calculate a mask from a given cubelist (such as 'is_in_ridge' or 'is_in_low_ss_layer')
These masks can then be applied to data for subsetting
"""
from __future__ import division
import iris
# need to work out how I want to deal with time objects
iris.FUTURE.cell_datetime_objects=True
import numpy as np

import pickle
import datetime


def low_static_stability_dictionary():
    """
    Load in the file produced by Ben detailing locations of LSLs
    :return: dictionary of dictionaries of lists of dictionaries of details of low static stability layers
    """
    fn = '/home/users/pr902839/datasets/nawdex/temp_for_jake/sondes_diags_sondes.pkl'
    return pickle.load(open(fn, 'rb'))


def LSL_condition(LSL_dictionary, cubelist, SS_Lim = 2):
    """
    Create mask for condition of profiles being within low static stability layers
    :param LSL_dictionary: Dictionary as created by Ben detailing all LSLs
    :param cubelist: a 2D cubelist
    :param SS_Lim: static stability limit to be considered low, integer in K/km, either 1 or 2 (default)
    :return: an array (or cube?) one where in LSL, zero otherwise
    a cube is the best way I can think of preserving the coordinates
    """
    # extract altitude profile
    altitude = cubelist.extract(iris.Constraint(name = 'altitude'))[0]
    # extract station identifiers
    source = altitude.attributes['origin']
    station_number = altitude.attributes['station_number']
    # extract an array of the vertical altitude coordinate
    alt = altitude.coord('altitude').points
    # create copy cube to put this new array into
    is_LSL = altitude.copy()

    for time in altitude.coord('time'):
        # need to make sure this actually loops over time and not altitude itself
        # convert 'time' to a datetime object
        time_dto = datetime.datetime(1970, 1, 1) + datetime.timedelta(hours = time.points[0])
        # define keys for dictionary
        filename = source + '_' + station_number + '_' + time_dto.strftime('%Y%m%d_%H%M') + '.nc'
        ### TIME IDENTIFICATION PROBLEM: STORED TIME COORDINATE IS ROUNDED ANALYSIS TIME ###
        ### FOR FILE IDENTIFICATION NEED RELEASE TIME TO BE STORED AS SCALAR CUBE ###
        levels = 'LSLs_' + str(SS_Lim) + 'p0K'

        # extract list of dictionaries of low static stability layers for this location and time
        levels_list = LSL_dictionary[filename][levels]

        #create array of zeros to be output
        is_LSL_array = np.zeros_like(alt)
        # for each low static stability layer
        for LSL in levels_list:
            # extract height of top and bottom of LSL in m
            h_bot = LSL['h_bot']*1e3
            h_top = LSL['h_top']*1e3
            # find indices of altitudes which are between these values
            indices = np.nonzero((alt > h_bot) * (alt < h_top))[0]
            # set these values to one
            is_LSL_array[indices] = 1
            # linearly interpolate for values either side (will have to then set requirement of >0.5 or >0.8 down the line)
            if indices[0] != 0:
                is_LSL_array[indices[0]-1] = (h_bot - alt[indices[0]-1])/(alt[indices[0]] - alt[indices[0]-1])
            if indices[-1] != len(is_LSL_array)-1:
                is_LSL_array[indices[-1]+1] = (alt[indices[-1]+1] - h_top)/(alt[indices[-1]+1] - alt[indices[-1]])

        # put this array as data into the appropriate time of the new cube
        is_LSL.extract(iris.Constraint(time = time))[0].data = is_LSL_array #!!!CHECK THIS WORKS!!!

    # add appropriate metadata to cube
    is_LSL.rename('mask_for_low_static_stability')
    is_LSL.long_name('truth_values_for_whether_point_in_low_static_stability_layer')
    is_LSL.units = ''

    return is_LSL


def ridge_trough_condition(cubelist, trop_reference_height):
    # need to first consider exactly how given the reference height we will define what is in a trough, and what is in a ridge
    # thought also required r.e. edges & transitions
    pass


def day_night_condition(cubelist):
    pass


def cloud_condition(cubelist):
    # much thought needed into how to decide what is a cloud
    pass
