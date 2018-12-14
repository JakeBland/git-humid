import iris
import iris.analysis
import numpy as np
import matplotlib.pyplot as plt

import sys
# Add the parent folder path to the sys.path list
sys.path.append('..')

from src.process_data import add_difference_fields

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
    
    
def scatter_plots(bin_width, variables):
    # have a seperate wrapper function which calls this and calculates difference fields if desired 'on the fly'
    """

    :param bin_width: number
    :param variables: array of variable names which will be represented by, in order:
                      x axis, y axis, marker colour, marker size, marker shape(?)
    """
    two_sec = station_code_list_two_sec()

    station_dic = {}

    first = True

    for code in two_sec:
        # read in data for desired variable
        cubelist = iris.load(
            '/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + model_type + '_2D_trop_relative.nc')
        # and sonde
        sonde_cubelist = iris.load(
            '/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + 'sonde' + '_2D_trop_relative.nc')

        cubelist = add_difference_fields(cubelist, sonde_cubelist)

        #cubelist of variables
        sub_list = cubelist.extract(iris.Constraint(name=variable))
        # can be used to determine whether the colour & shape will be variable
        var_indicator = len(sub_list)




