
import iris

from read_files import read_data
import calculate
from re_grid import re_grid_1d
from my_filters import my_filter

def temperature_cube(cubelist):
    """
    Create cube of temperature
    :param cubelist: list of cubes containing pressure and theta
    :return: cube of temperature
    """
    theta = cubelist.extract(iris.Constraint(name='air_potential_temperature'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    # [0] required as cubelist.extract returns a cube list

    temp = calculate.temp_from_theta(theta, pressure)

    temperature = theta.copy()
    temperature.standard_name = 'air_temperature'
    temperature.data = temp

    return temperature


def trop_height(cubelist, filter_dic, kind = 'linear'):
    """
    Function to calculate tropopause height from re-gridded & smoothed temperature
    :param cubelist: list of cubes containing temperature and altitude
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: cube of tropopause height in metres
    """
    temp = cubelist.extract(iris.Constraint(name='air_temperature'))[0]
    altitude = cubelist.extract(iris.Constraint(name='altitude'))[0]
    # [0] required as cubelist.extract returns a cube list

    uniform_height_temp = re_grid_1d(temp, altitude, 0, 20000, 10, kind)
    # re-grid temp to 10m in vertical to 20km
    filtered_temp = my_filter(uniform_height_temp.data, filter_dic)
    # filter to smooth out noise
    trop_alt = calculate.tropopause_height(filtered_temp, range(0, 20000, 10))
    # calculate tropopause altitude
    return iris.cube.Cube(trop_alt, standard_name = 'tropopause_altitude', units = 'm',
            aux_coords_and_dims = [(temp.coord('latitude'), None), (temp.coord('longitude'), None), (temp.coord('time'), None)])


def process_single_ascent(source, station_number, time, type, filter_dic, lead_time = 0, kind = 'linear'):
    """
    File to do the stuff
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: string, 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param type: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param lead_time: time in days before the verification time that the forecast was started
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return:
    """
    variables = ['air_pressure', 'air_temperature', 'air_potential_temperature', 'dew_point_temperature', 'specific_humidity', 'altitude']
    # not all types will have all variables, this will be dealt with later

    cubelist = read_data(source, station_number, time, variables, type, lead_time)

    if type == 'UKMO':
        # files do not have a temperature field, so we must calculate one
        cubelist.append(temperature_cube(cubelist))

    cubelist.append(trop_height(cubelist, filter_dic, kind))
    # re-grid temperature to 10m in vertical up to 20km
    # filter the temperature
    # calculate the tropopause height
    # add trop_height_m as cube to list

    altitude = cubelist.extract(iris.Constraint(name = 'altitude'))
    trop_alt = cubelist.extract(iris.Constraint(name = 'tropopause_altitude'))
    altitude.data -= trop_alt.data
    # subtract trop_height_m from altitude data

    cubelist_reg = re_grid_1d(cubelist, altitude, -10000, 10000, 10)
    # re-grid all variables to 10m spacing +/- 10km of tropopause
    # re-gridding the original temperature as opposed to the previously filtered one

    
    # filter all variables

    # produce a plot comparing all 5(?) different temperature profiles & showing calculated trop height

    #

