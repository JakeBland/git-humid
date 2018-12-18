import iris
import iris.analysis
import numpy as np
import matplotlib.pyplot as plt

import sys
# Add the parent folder path to the sys.path list
sys.path.append('..')

from src.process_data import add_difference_fields
from src import make_cubes

def station_code_list_two_sec():

    return ['EMN_02365', 'EMN_02527', 'EMN_03005',
               'EMN_03238', 'EMN_03354', 'EMN_03808',
               'EMN_03882', 'EMN_03918', 'EMN_04270', 'EMN_04320',
               'EMN_04339', 'EMN_04360', 'EMN_06011', 'EMN_10035',
               'EMN_10113', 'EMN_10184', 'EMN_10238', 'EMN_10393',
               'EMN_10410', 'EMN_10548', 'EMN_10618', 'EMN_10739',
               'EMN_10771', 'EMN_10868', 'DLR_04018', 'IMO_04018', 'NCAS_03501']


def profile_wrap(model_type, variable):

    two_sec = station_code_list_two_sec()

    station_dic = {}

    first = True

    for code in two_sec:
        # read in data for desired variable
        cubelist = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + model_type + '_2D_trop_relative.nc')
        # and sonde
        sonde_cubelist = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + 'sonde' + '_2D_trop_relative.nc')

        cubelist = add_difference_fields(cubelist, sonde_cubelist)
        # the idea is that adding the difference fields should be relatively fast
        # and that it may be more efficient to calculate them every time than to save them
        # and load files which are now much larger

        cube = cubelist.extract(iris.Constraint(name = variable))[0]

        # then take the average over all times for a single station, leaving an average vertical profile
        # note: I am concerned here about the handling of np.nan values
        cube_mean = cube.collapsed('time', iris.analysis.MEAN)

        if first:

            altitude = cube_mean.coord('altitude')
            first = False

        # put these values into a dictionary of dictionaries
        station_dic[code] = cube
    # create empty array for mean & st.dev

    for n, key in enumerate(station_dic):
        if not n:
            profile_array = np.array([station_dic[key].data])
        else:
            profile_array = np.append(profile_array, [station_dic[key].data], axis = 0)
    
    all_mean = np.nanmean(profile_array, axis=0)
    all_stdev = np.std(profile_array, axis=0)

    fig, ax = plt.subplots()

    #ax.fill([[all_mean[0]], all_mean-all_stdev, [all_mean[-1]], np.flipud(all_mean+all_stdev)], [, altitude.points, np.flipud(altitude.points)])
    ax.plot([0, 0], [-1e4, 1e4], color = 'b')
    ax.plot([-1, 1], [0, 0], color = 'b')
    
    for key in station_dic:

        ax.plot(station_dic[key].data, altitude.points, color = [.4, .4, .4])

    ax.plot(all_mean, altitude.points, color = 'k', linewidth = 3)

    ax.plot(all_mean - all_stdev, altitude.points, color = 'r')
    ax.plot(all_mean + all_stdev, altitude.points, color = 'r')
    
    plt.title(model_type + '_' + variable)
    plt.ylabel('tropopause_relative_altitude, m')
    plt.xlabel(variable)
    
    plt.savefig('/home/users/bn826011/PhD/figures/' +
                model_type + '_' + variable + '_profile.jpg')
    
    
def scatter_plots(model_type, variables, bin_width = 500, max_size = 20, alpha = .5):
    # have a seperate wrapper function which calls this and calculates difference fields if desired 'on the fly'
    """

    :param bin_width: number
    :param variables: array of variable names which will be represented by, in order:
                      x axis, y axis, marker colour, marker size, marker shape(?)
                      must be name of variable in cube, optionally suffixed with
                      '_difference', '_fractional_difference' or '_normalised_difference'
    """
    two_sec = station_code_list_two_sec()

    first = True

    for code in two_sec:
        # read in data for desired variable
        cubelist = iris.load(
            '/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + model_type + '_2D_trop_relative.nc')
        # and sonde
        sonde_cubelist = iris.load(
            '/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + 'sonde' + '_2D_trop_relative.nc')

        #cubelist = add_difference_fields(cubelist, sonde_cubelist)

        if first:
            altitude = cubelist.extract(iris.Constraint(name = 'air_pressure'))[0].coord('altitude')
            first = False
            # only need to read altitude coordinate once

            bin_low_bound = np.arange(np.min(altitude.points), np.max(altitude.points), bin_width)
            # create array of lower bounds for height bins

            bin_var_dic = {}

            for variable in variables:

                bin_var_dic[variable] = np.array([])
                # create dictionary of values of variable for each bin
                
                
        #cubelist of variables
        data_dic = {}
        for variable in variables:
            if variable == 'altitude_tropopause_relative':
                data_dic[variable] = altitude.points
            if 'difference' in variable:
                cube = make_cubes.difference_fields_selective(cubelist, sonde_cubelist, variable)
                data_dic[variable] = cube.data
                cubelist.append(cube)
            else:
                data_dic[variable] = cubelist.extract(iris.Constraint(name=variable))[0].data
        # can be used to determine whether the colour & shape will be variable
        var_indicator = len(data_dic)
        

        for lb in bin_low_bound:

            for variable in variables:
                #print sub_list.extract(iris.Constraint(name = variable))[0]
                #print (altitude.points >= lb)*(altitude.points < lb + bin_width)
                #print sub_list.extract(iris.Constraint(name = variable))[0].data[:,(altitude.points >= lb)*(altitude.points < lb + bin_width)]
                bin_var_dic[variable] = np.append(bin_var_dic[variable], np.nanmean(data_dic[variable][:,(altitude.points >= lb)*(altitude.points < lb + bin_width)], axis = 1))
                # the 'axis=1' means that the average is only spatial and not temporal
                
    # if colour and size are to be specified by variables, do this here

    if var_indicator > 2:

        colour = bin_var_dic[variables[2]]

        if var_indicator > 3:

            size = bin_var_dic[variables[3]]

            sizemax = np.nanmax(np.abs(size))

            size_norm = max_size*size/sizemax
            # normalise marker size to below specified maximum

        else:

            size_norm = max_size/2

    else:

        colour = None
        
    plt.figure(figsize = (12, 12))

    plt.scatter(bin_var_dic[variables[0]], bin_var_dic[variables[1]], s = size_norm, c = colour, alpha = alpha, edgecolors = 'face')

    plt.colorbar()
    






