import iris
import iris.analysis
import numpy as np
import matplotlib.pyplot as plt

def station_code_list_two_sec():

    return ['EMN_02365', 'EMN_02527',#'EMN_03005', 
               'EMN_03238', 'EMN_03354', 'EMN_03808',
               'EMN_03882', 'EMN_03918', 'EMN_04270', 'EMN_04320',
               'EMN_04339', 'EMN_04360', 'EMN_06011', 'EMN_10035',
               'EMN_10113', 'EMN_10184', 'EMN_10238', 'EMN_10393',
               'EMN_10410', 'EMN_10548', 'EMN_10618', 'EMN_10739',
               'EMN_10771', 'EMN_10868', 'DLR_04018', 'IMO_04018', 'NCAS_03501']


def profile_plots(model_type = 'ukmo', variable = 'specific_humidity', difference = None):

    two_sec = station_code_list_two_sec()

    station_dic = {}

    first = True

    for code in two_sec:
        # read in data for desired variable
        model = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + model_type + '_2D_trop_relative.nc',variable)[0]
        # read in altitude for the first one
        if first:
            altitude = model.coord('altitude')
            first = False
        # here is where one would read in and apply a filter if desired

        # then take the average over all times for a single station, leaving an average vertical profile
        # note: I am concerned here about the handling of np.nan values
        model_mean = model.collapsed('time', iris.analysis.MEAN)

        # and do this for sonde if a difference is requested
        if difference:
            sonde = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/sonde_2D_trop_relative.nc', variable)[0]
            # filter here (optional)
            sonde_mean = sonde.collapsed('time', iris.analysis.MEAN)

            if difference == 'fractional':

                cube = (model_mean - sonde_mean)/sonde_mean
                cube.rename(variable + '_fractional_difference')
                dlab = 'fractional_difference'

            else:

                cube = model_mean - sonde_mean
                cube.rename(variable + '_difference')
                dlab = 'difference'

        else:

            cube = model_mean
            dlab = ''

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
    
    plt.title(model_type + '_' + variable + '_' + dlab)
    plt.ylabel('tropopause_relative_altitude, m')
    plt.xlabel(variable + ' ' + dlab)
    
    plt.savefig('/home/users/bn826011/PhD/git_humid/sonde_humid_proj/figures/' +
                model_type + '_' + variable + '_' + dlab + '_profile.jpg')
    
    
def scatter_plots(bin_width, variable_x, variable_y, variable_colour = None, variable_size = None, variable_shape = None):
    # this is why the cubelists need to have seperate difference fields - need to re-run

    two_sec = station_code_list_two_sec()

    station_dic = {}

    first = True

    for code in two_sec:
        # read in data for desired variable
        model = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/' + model_type + '_2D_trop_relative.nc',variable)[0]
        # read in altitude for the first one
        if first:
            altitude = model.coord('altitude')
            first = False
        # here is where one would read in and apply a filter if desired

        # then take the average over all times for a single station, leaving an average vertical profile
        # note: I am concerned here about the handling of np.nan values
        model_mean = model.collapsed('time', iris.analysis.MEAN)

        # and do this for sonde if a difference is requested
        if difference:
            sonde = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/' + code + '/sonde_2D_trop_relative.nc', variable)[0]
            # filter here (optional)
            sonde_mean = sonde.collapsed('time', iris.analysis.MEAN)

            if difference == 'fractional':

                cube = (model_mean - sonde_mean)/sonde_mean
                cube.rename(variable + '_fractional_difference')

            else:

                cube = model_mean - sonde_mean
                cube.rename(variable + '_difference')

        else:

            cube = model_mean




