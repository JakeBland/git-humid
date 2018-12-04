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
    :param type: string, origin of data: 'sonde', 'UKMO', 'ECAN'
    :param flag: number, 0 when things are working well, 
                 and asigned to a number when somthing goes wrong
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param lead_time: time in days before the verification time that the forecast was started
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: CubeList of smoothed vertical profiles
    """
    variables = ['air_pressure', 'air_temperature', 'air_potential_temperature', 
                 'dew_point_temperature', 'specific_humidity', 'altitude', 
                 'mass_fraction_of_cloud_ice_in_air', 'mass_fraction_of_cloud_liquid_water_in_air']
    # not all types will have all variables, this will be dealt with later

    cubelist = read_data(source, station_number, time, variables, dtype, lead_time)

    # calculate variables such that all profiles will have, as a minimum, 
    # fields of altitude, p, T, theta, q, RHi and RHw
    if dtype == 'UKMO':
        cubelist.append(make_cubes.temperature_cube(cubelist))
    else:
        cubelist.append(make_cubes.theta_cube(cubelist))
        pass

    if dtype == 'sonde':
        cubelist.append(make_cubes.specific_humidity_cube(cubelist))
        pass

    cubelist.append(make_cubes.relative_humidity_cube(cubelist, 'liquid_water'))
    cubelist.append(make_cubes.relative_humidity_cube(cubelist, 'ice'))

    # filter all variables using kernel smoothing [only sonde]
    if dtype == 'sonde':
        altitude = cubelist.extract(iris.Constraint(name='altitude'))[0]
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


def process_regridded_dictionary(source, station_number, time, filter_dic, kind = 'linear'):
    """
    Now data has been put onto new vertical coordinate, calculate vertical 
    derivatives & re-grid these onto same new vertical coordinate
    :param source:
    :param station_number:
    :param time:
    :param filter_dic:
    :param kind:
    :return:
    """
    pass
    # read in cubelist dictionary

    # calculate dtheta/dz

    # calculate N**2 = g/theta dtheta/dz

    # calculate dq/dz and 1/q dq/dz

    # I'm sure there was another useful derivative, that I forgot to write down

    # return a cubelist_dic with the new variables