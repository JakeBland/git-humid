"""
Collection of functions to add desired variables to the cubelists
Sort of 'wrapper functions' for my_filters, calculate & make_cubes
"""

import iris

from read_files import read_data
from my_filters import filter_cubelist
import make_cubes
import calculate


def process_single_ascent(source, station_number, time, dtype, filter_dic, 
                          flag, lead_time = 0, kind = 'linear'):
    """
    Produce list of filtered variables which can be calculated 
    without derivatives from given data
    :param source: Code representing origin of data, options for which are: 
                   'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: string, 4-6 digit identifier of particular station 
                           from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param dtype: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :param flag: number, 0 when things are working well, 
                 and asigned to a number when somthing goes wrong
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param lead_time: time in days before the verification time that the forecast was started
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: CubeList of smoothed vertical profiles
    """
    variables = ['air_pressure', 'air_temperature', 'air_potential_temperature', 
                 'dew_point_temperature', 'specific_humidity', 'altitude', 
                 'mass_fraction_of_cloud_ice_in_air', 'mass_fraction_of_cloud_liquid_water_in_air'
                 'latitude', 'longitude']
    # not all types will have all variables, this will be dealt with later

    cubelist = read_data(source, station_number, time, variables, dtype, lead_time)

    # calculate variables such that all profiles will have, as a minimum, 
    # fields of altitude, p, T, theta, q, RHi and RHw
    cubelist = add_humidity_fields(cubelist, dtype)

    altitude = cubelist.extract(iris.Constraint(name='altitude'))[0]
    # filter all variables using kernel smoothing [only sonde]
    if dtype == 'sonde':
        cubelist.remove(altitude)
        # as the vertical coordinate I don't think we want this smoothed (?) (can always remove this line)
        cubelist_smooth = filter_cubelist(cubelist, altitude, filter_dic)
        cubelist_smooth.append(altitude)
    else:
        cubelist_smooth = cubelist

    # calculate the tropopause height
    # add trop_height_m as cube to list
    temperature = cubelist_smooth.extract(iris.Constraint(name='air_temperature'))[0]
    trop_alt, flag = calculate.tropopause_height(temperature.data, altitude.data, flag)[:-1]
    cubelist_smooth.append(iris.cube.Cube(trop_alt, standard_name = 'tropopause_altitude', 
                                          units = 'm', aux_coords_and_dims = 
                                          [(altitude.coord('latitude'), None), 
                                           (altitude.coord('longitude'), None), 
                                           (altitude.coord('time'), None)]))

    return cubelist_smooth, flag


def add_humidity_fields(cubelist, dtype):
    """
    Calculate variables and add to cubelists such that all lists will have, as a minimum,
    fields of altitude, p, T, theta, q, RHi, RHw and RH
    :param cubelist: list of cubes
    :param dtype: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :return: extended list of cubes with specified minimum fields
    """
    if dtype == 'UKMO':
        cubelist.append(make_cubes.temperature_cube(cubelist))
    else:
        cubelist.append(make_cubes.theta_cube(cubelist))

    if dtype == 'sonde':
        cubelist.append(make_cubes.specific_humidity_cube(cubelist))

    cubelist.append(make_cubes.relative_humidity_cube(cubelist, 'liquid_water'))
    cubelist.append(make_cubes.relative_humidity_cube(cubelist, 'ice'))
    cubelist.append(make_cubes.relative_humidity_cube(cubelist, 'mixed'))

    return cubelist


def process_concatenated(cubelist_dic):
    """
    Now data has been put onto new vertical coordinate, and concatentated
    along time, calculate vertical derivatives and also difference fields
    :param cubelist_dic: dictionary of 2D cubelists
    :return: dictionary of extended cubelists with gradient fields
    """
    for key in cubelist_dic:
        cubelist = cubelist_dic[key]
        cubelist = add_gradient_fields(cubelist)

    #     if key == 'sonde':
    #
    #         sonde_cubelist = cubelist
    #
    # for key in cubelist_dic:
    #
    #     if key != 'sonde':
    #         cubelist = cubelist_dic[key]
    #         cubelist = add_difference_fields(cubelist, sonde_cubelist)

    # It is probably more sensible to calculate difference fields within plotting functions
    # to avoid saving unnecessarily large files

    return cubelist_dic


def add_gradient_fields(cubelist):
    """
    Add gradient fields to cubelist
    :param cubelist: list of cubes containing altitude, theta & specific_humidity
    :return: longer list of cubes with gradient fields
    """
    cubelist.append(make_cubes.theta_gradient_cube(cubelist))
    cubelist.append(make_cubes.Brunt_Vaisala_square_cube(cubelist))
    cubelist.append(make_cubes.q_gradient_cube(cubelist))
    cubelist.append(make_cubes.fractional_humidity_gradient_measure_cube(cubelist))
    # I'm sure there was another useful derivative, that I forgot to write down

    return cubelist


def add_difference_fields(cubelist, sonde_cubelist):
    """
    Probably redundant function to add difference fields to a cubelist
    """

    for var_name in ['air_temperature', 'air_potential_temperature', 'pressure',
                     'potential_temperature_vertical_gradient', 'square_of_brunt_vaisala_frequency_in_air',
                     'fractional_specific_humidity_gradient']:

        cubelist.append(make_cubes.difference_cube(cubelist, sonde_cubelist, var_name))

    for var_name in ['specific_humidity', 'relative_humidity', 'specific_humidity_vertical_gradient']:

        cubelist.append([make_cubes.difference_cube(cubelist, sonde_cubelist, var_name, fractional=True, normalised=True)])

    return cubelist