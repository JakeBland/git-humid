"""
Collection of functions to re-grid data to specified uniform height scale
"""

import iris
from scipy.interpolate import interp1d

from process_data import process_single_ascent

def re_grid_1d(variables, dimension, lower, upper, spacing, kind = 'linear'):
    """
    Take a set of variables defined along a dimension and re-grid them to a uniform scale
    :param variables: list of cubes for the variables
    :param dimension: cube of previous dimension: monotonic and of the same length as variables
    :param lower: number, lower bound of uniform scale
    :param upper: number, upper bound of uniform scale
    :param spacing: number, spacing of uniform scale
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: list of cubes of new variables
    """
    new_dimension = range(lower, upper+1, int(spacing))
    # create evenly spaced array for new dimension

    new_dim = iris.coords.DimCoord(new_dimension, standard_name = dimension.standard_name,
                                   units = dimension.units)

    lat = variables[0].coord('latitude')
    lon = variables[0].coord('longitude')
    time = variables[0].coord('time')
    # read coords of lat, lon & time from the first variable (as they should all be the same)

    new_cubes = iris.cube.CubeList([])

    for cube in variables:

        if cube.shape == (1,) or cube.shape == ():
            # these cubes do not have dimension
            new_cubes.append(cube)
            # just add them to new cube
        else:

            interp_2_new_dim = interp1d(dimension.data, cube.data, kind, bounds_error = False)
            new_data = interp_2_new_dim(new_dimension)
            # interpolate to new dimension array

            new_cubes.append(iris.cube.Cube(new_data, standard_name=cube.standard_name, 
                                            long_name=cube.long_name, var_name=cube.var_name, 
                                            units=cube.units, attributes=cube.attributes,
                                            dim_coords_and_dims=[(new_dim, 0)], 
                                            aux_coords_and_dims=[(lat,None), (lon,None), 
                                                                 (time,None)]))
             # create cube of new interpolated variable on new dimcoord and append to list

    return new_cubes


def re_grid_trop_0(source, station_number, time, filter_dic, kind = 'linear', throw_flag = True):
    """
    Take data from all sources
    :param source: Code representing origin of data, options for which are: 
                   'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: string, 4-6 digit identifier of particular station 
                           from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param flag: number, 0 when things are working well, 
                 and assigned to a number when something goes wrong
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :param throw_flag: if True, return False if flag is raised by sonde ascent.
    :return: dictionary of cubelists for the sonde, ukmo analysis and 1, 3 and 5 
             day forecasts, and ECMWF analyses
    """

    sonde, flag_sonde = process_single_ascent(source, station_number, time, 'sonde', filter_dic, 0)

    if throw_flag:
        if flag_sonde:
            return False
    # if throw_flag, disregard the ascent if any error occurred in the processing of sonde data

    ukmo, flag_ukmo = process_single_ascent(source, station_number, time, 'UKMO', filter_dic, 0)
    ukmo1 = process_single_ascent(source, station_number, time, 'UKMO', filter_dic, 0, lead_time = 1)[0]
    ukmo3 = process_single_ascent(source, station_number, time, 'UKMO', filter_dic, 0, lead_time=3)[0]
    ukmo5 = process_single_ascent(source, station_number, time, 'UKMO', filter_dic, 0, lead_time=5)[0]
    ecan, flag_ecan = process_single_ascent(source, station_number, time, 'ECAN', filter_dic, 0)

    trop_const = iris.Constraint(name = 'tropopause_altitude')
    alt_const = iris.Constraint(name = 'altitude')

    trop_alt = sonde.extract(trop_const)[0].data
    
#    ###
#    sonde_top = sonde.extract(alt_const)[0].data[-1]
#    print('Top of profile : ' + str(sonde_top) + ' m, tropopause found at : ' +
#              str(trop_alt) + ' m.')
#    ###

    if flag_sonde:

        sonde_top = sonde.extract(alt_const)[0].data[-1]
        print(source + '_' + station_number + '_' + time.strftime('%Y%m%d_%H%M') + 
              ' sonde could not identify tropopause ' + 'below 2km below top of profile. ' + 
              '\n Top of profile : ' + str(sonde_top) + ' m, tropopause found at : ' +
              str(trop_alt) + ' m. \n Instead trying to find tropopause from UKMO data.')

        trop_alt = ukmo.extract(trop_const)[0].data
        
        ###
        ukmo_top = ukmo.extract(alt_const)[0].data[-1]
        print('Top of UKMO profile : ' + str(ukmo_top) + ' m, tropopause found at : ' +
              str(trop_alt) + ' m.')
        ###

        if flag_ukmo:

            ukmo_top = ukmo.extract(alt_const)[0].data[-1]
            print(source + '_' + station_number + '_' + time.strftime('%Y%m%d_%H%M') + 
                  ' sonde could not identify tropopause ' + 'below 2km below top of profile. ' + 
                  '\n Top of profile : ' + str(ukmo_top) + ' m, tropopause found at : ' +
                  str(trop_alt)+ ' m. \n Instead trying to find tropopause from ECAN data.')

            trop_alt = ecan.extract(trop_const)[0].data
            
            ###
            ecan_top = ecan.extract(alt_const)[0].data[-1]
            print('Top of ECAN profile : ' + str(ecan_top) + ' m, tropopause found at : ' +
                  str(trop_alt) + ' m.')
            ###

            if flag_ecan:

                ecan_top = ecan.extract(alt_const)[0].data[-1]
                print(source + '_' + station_number + '_' + time.strftime('%Y%m%d_%H%M') + 
                      ' sonde could not identify tropopause ' + 'below 2km below top of profile. ' + 
                      '\n Top of profile : ' + str(ecan_top) + ' m, tropopause found at : ' +
                      str(trop_alt) + ' m. \n Due to lack of tropopause found, this profile cannot be used')

                return False

    cubelist_dic = {'sonde':sonde, 'ukmo':ukmo, 'ukmo1':ukmo1, 'ukmo3':ukmo3, 'ukmo5':ukmo5, 'ecan':ecan}

    for key in cubelist_dic:
        
        cubelist = cubelist_dic[key]

        reference_altitude = cubelist.extract(alt_const)[0].copy()
        # this .copy() is important s.t. geometric altitude is preserved as a cube

        reference_altitude.data = reference_altitude.data - trop_alt

        cubelist_dic[key] = re_grid_1d(cubelist, reference_altitude, -10000, 10000, 10, kind)

    return cubelist_dic
    # it would be nice to produce a plot of superimposed temperature profiles, with dotted tropopauses to compare