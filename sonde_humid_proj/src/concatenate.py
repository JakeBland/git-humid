"""
File to take dictionaries of cubelists across all time and concatenate them into one big dictionary of all data
from a given single site in Sept/Oct 2016
"""
import datetime
import iris
from re_grid import re_grid_trop_0

def create_datetime_list(source, station_number):
    """
    Create lists of datetime objects corresponding to the times of radiosonde
    launches, and closest analysis times
    :param folder:
    :param station_number:
    :return:
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


def concatenate_cubelist_dictionary(source, station_number, filter_dic, kind = 'linear'):
    # output dictionary of 2D cubelists in time & alt
    pass

    datetime_list = create_datetime_list(source, station_number)

    # for the first time, create first cubelist_dic
    cubelist_dictionary = re_grid_trop_0(source, station_number, datetime_list[0], filter_dic, kind)
    # this will actually be '= process_regridded_dictionary(source, station_number, etc.)' once I write it

    # for the rest of the times
    for time in datetime_list[1:]:

        # create new cubelist_dic
        new_cubelist_dic = re_grid_trop_0(source, station_number, time, filter_dic, kind)
        # for each key in dictionary:
        for key in cubelist_dictionary:
            # extend each cubelist in first dictionary by new one
            cubelist_dictionary[key].extend(new_cubelist_dic[key])

    twoD_cubelist_dictionary = {}

    # for each key in dictionary:
    for key in cubelist_dictionary:
        # will possibly have to do stuff to homogenise cubes, but this should have been done prior in the re-gridding stage

        # concatenate cubelist along time dimension
        twoD_cubelist_dictionary[key] = cubelist_dictionary[key].merge()
        # actually either need to use merge, or add new time dimension coord
        assert len(twoD_cubelist_dictionary[key]) == len(new_cubelist_dic[key])

        # save_folder = 
        # where do I actually have space to save one of these for each site???

        #iris.save(twoD_cubelist_dictionary[key], save_folder + '/' + key + '_2D_trop_relative.nc')

    return twoD_cubelist_dictionary
    # but don't actually return if it has actually saved