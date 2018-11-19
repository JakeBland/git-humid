
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


def trop_height(cubelist, filter_, kind = 'linear'):
    # make sure this isn't called the same thing as the function in 'calculate'

    temp = cubelist.extract(iris.Constraint(name='air_temperature'))[0]
    altitude = cubelist.extract(iris.Constraint(name='altitude'))[0]
    # [0] required as cubelist.extract returns a cube list

    uniform_height_temp = re_grid_1d(temp, altitude, 0, 20000, 10, kind)

    filtered_temp = my_filter(uniform_height_temp.data, filter_)

    return calculate.tropopause_height(filtered_temp, range(0, 20000, 10))


def process_single_ascent(source, station_number, time, type, filter_, lead_time = 0, kind = 'linear'):
    """
    File to do the stuff
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: string, 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param type: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :param filter:
    :param lead_time:
    :param kind:
    :return:
    """

    variables = ['air_pressure', 'air_temperature', 'air_potential_temperature', 'dew_point_temperature', 'specific_humidity', 'altitude']
    # not all types will have all variables, this will be dealt with later

    cubelist = read_data(source, station_number, time, variables, type, lead_time)

    if type == 'UKMO':
        # files do not have a temperature field, so we must calculate one
        cubelist.append(temperature_cube(cubelist))

    trop_height(cubelist, filter_, kind)
    # re-grid temperature to 10m in vertical up to 20km
    # filter the temperature
    # calculate the tropopause height

    # re-grid all variables to 10m spacing +/- 10km of tropopause
    # re-gridding the original temperature as opposed to the previously filtered one

    # filter all variables

    # produce a plot comparing all 5(?) different temperature profiles & showing calculated trop height

    #

