"""
File to take dictionaries of cubelists across all time and concatenate them 
into one big dictionary of all data from a given single site in Sept/Oct 2016
"""
import datetime
import iris
from re_grid import re_grid_trop_0
from process_data import add_gradient_fields

#from iris.experimental.equalise_cubes import equalise_attributes
#from iris.util import unify_time_units
# these are fixes for merging and concatenation, but should not be needed if
# cubes are prepared properly from reading in

def create_datetime_list(source, station_number):
    """
    Create lists of datetime objects corresponding to the times of radiosonde launches
    :param source: Code representing origin of data, options for which are: 
                   'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: 4-6 digit identifier of particular station from which 
                           sonde was released
    :return: list of datetime objects corresponding to times of radiosonde 
             released for a given particular location
    """
    with open('../File_lists/' + source + '_' + station_number + '_list.txt', 'r') as myfile:
        file_list = myfile.readlines()
    # create list of names of files for radiosonde data for herstmonceux

    datetime_list = []
    # create lists of datetime objects which can be used to identify file names

    for file_name in file_list:

        date_time = file_name[-17:-4]
        # remove the five characters '.nc\n' from end
        # and select the 13 character date and time preceeding that

        dto = datetime.datetime.strptime(date_time, '%Y%m%d_%H%M')
        # convert this string into datetime object

        if dto.hour in [10, 11, 12, 22, 23, 00]:
            # Only launches which will be compared to model time 00 or 12
            # In order to have UKMO forecasts to compare to at 1, 3 and 5 day lead times
            datetime_list.append(dto)

    return datetime_list


def concatenate_cubelist_dictionary(source, station_number, filter_dic = {'name' : 'kernel', 
                   'gaussian_half_width' : 50, 'window_half_width' : 200}, kind = 'linear'):
    """
    Concatenate sondes from same location at different times into single object
    :param source: Code representing origin of data, options for which are: 
                   'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: 4-6 digit identifier of particular station from which 
                           sonde was released
    :param filter_dic: dictionary specifying filter name and necessary parameters
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: dictionary of cubelists for the sonde, ukmo analysis and 1, 3 and 5 
             day forecasts, and ECMWF analyses, where cubes in cubelist have 
             dimensions of altitude and time
    """
    # output dictionary of 2D cubelists in time & alt
    datetime_list = create_datetime_list(source, station_number)
    
    if not datetime_list:
        return source + '_' + station_number + ' ascents not found'

    # for the first time, create first cubelist_dic
    cubelist_dictionary = re_grid_trop_0(source, station_number, datetime_list[0], 
                                                              filter_dic, kind)

    # for the rest of the times
    for time in datetime_list[1:]:

        # create new cubelist_dic
        new_cubelist_dic = re_grid_trop_0(source, station_number, time, filter_dic, kind)
        
        if new_cubelist_dic:
            # it will return False if there is no found tropopause
        
            # for each key in dictionary:
            for key in cubelist_dictionary:
                # extend each cubelist in first dictionary by new one
                cubelist_dictionary[key].extend(new_cubelist_dic[key])

    twoD_cubelist_dictionary = {}

    # for each key in dictionary:
    for key in cubelist_dictionary:
        # will possibly have to do stuff to homogenise cubes, but this should 
        # have been done prior in the re-gridding stage
        
        # concatenate cubelist along time dimension
        twoD_cubelist_dictionary[key] = cubelist_dictionary[key].merge()
        # actually either need to use merge, or add new time dimension coord
        #assert len(twoD_cubelist_dictionary[key]) == len(new_cubelist_dic[key])

        # add gradient fields to cube list
        twoD_cubelist_dictionary[key] = add_gradient_fields(twoD_cubelist_dictionary[key])

        save_folder = '/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/' + source + '_' + station_number
        # where do I actually have space to save one of these for each site???

        iris.save(twoD_cubelist_dictionary[key], save_folder + '/' + key + '_2D_trop_relative.nc')

    #return twoD_cubelist_dictionary
    # but don't actually return if it has actually saved