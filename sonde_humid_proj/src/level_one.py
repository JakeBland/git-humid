"""
This file is now old and redundant, but will be kept for reference for the time being
"""

import iris
import numpy as np

from read_files import read_data
import calculate
from re_grid import re_grid_1d
from my_filters import my_filter, filter_cubelist

import sys
# Add the parent folder path to the sys.path list
sys.path.append('..')

from plot.temperature_profiles import temperature_profile_comparison_plot


def temperature_cube(cubelist):
    """
    Create cube of temperature
    :param cubelist: list of cubes containing pressure and theta
    :return: cube of temperature
    """
    theta = cubelist.extract(iris.Constraint(name='air_potential_temperature'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    # [0] required as cubelist.extract returns a cube list

    temp = calculate.temp_from_theta(theta.data, pressure.data)

    temperature = theta.copy()
    temperature.standard_name = 'air_temperature'
    temperature.data = temp

    return temperature


def trop_height(cubelist, filter_dic, flag, kind = 'linear'):
    """
    Function to calculate tropopause height from re-gridded & smoothed temperature
    :param cubelist: list of cubes containing temperature and altitude
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param flag:
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: cube of tropopause height in metres
    """
    temp = cubelist.extract(iris.Constraint(name='air_temperature'))
    altitude = cubelist.extract(iris.Constraint(name='altitude'))[0]
    # [0] required for altitude as cubelist.extract returns a cube list

    uniform_height_temp = re_grid_1d(temp, altitude, 0, 20001, 10, kind)[0]
    # re-grid temp to 10m in vertical to 20km
    # [0] required as it returns a cube list
    filtered_temp = my_filter(uniform_height_temp.data, filter_dic)
    # filter to smooth out noise
    trop_alt, flag = calculate.tropopause_height(filtered_temp, np.array(range(0, 20001, 10)), flag)[:-1]
    print trop_alt
    # calculate tropopause altitude, only taking the first returned valie
    return iris.cube.Cube(trop_alt, standard_name = 'tropopause_altitude', units = 'm',
            aux_coords_and_dims = [(altitude.coord('latitude'), None), (altitude.coord('longitude'), None), (altitude.coord('time'), None)]), flag


def process_single_ascent(source, station_number, time, dtype, filter_dic, flag, lead_time = 0, kind = 'linear'):
    """
    File to do the stuff
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: string, 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param type: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :param flag:
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param lead_time: time in days before the verification time that the forecast was started
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return:
    """
    variables = ['air_pressure', 'air_temperature', 'air_potential_temperature', 'dew_point_temperature', 'specific_humidity', 'altitude']
    # not all types will have all variables, this will be dealt with later

    cubelist = read_data(source, station_number, time, variables, dtype, lead_time)

    if dtype == 'UKMO':
        # files do not have a temperature field, so we must calculate one
        cubelist.append(temperature_cube(cubelist))

    trop_alt, flag = trop_height(cubelist, filter_dic, flag, kind)
    cubelist.append(trop_alt)
    # re-grid temperature to 10m in vertical up to 20km
    # filter the temperature
    # calculate the tropopause height
    # add trop_height_m as cube to list

    altitude = cubelist.extract(iris.Constraint(name = 'altitude'))[0]
    trop_alt = cubelist.extract(iris.Constraint(name = 'tropopause_altitude'))[0]
    dummy_altitude = altitude.data - trop_alt.data
    altitude.data = dummy_altitude
    # subtract trop_height_m from altitude data

    cubelist_reg = re_grid_1d(cubelist, altitude, -10000, 10001, 10, kind)
    # re-grid all variables to 10m spacing +/- 10km of tropopause
    # re-gridding the original temperature as opposed to the previously filtered one

    cubelist_smooth = filter_cubelist(cubelist_reg, filter_dic)
    # filter all variables

    temperature_profile_comparison_plot(cubelist, cubelist_reg, cubelist_smooth, kind, filter_dic)
    # produce a plot comparing all 5(?) different temperature profiles & showing calculated trop height

    # if dtype == sonde calculate specific humidity and add to sonde cubelist

