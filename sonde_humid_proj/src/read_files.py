
import iris


def sonde_filepath(source):

    return '/home/users/pr902839/datasets/nawdex/radiosondes/' + source + '/netcdf/'


def sonde_filename(source, station_number, time):

    return source + '_' + station_number + '_' + time.strftime('%Y%m%d_%H%M') + '.nc'


def read_sonde_data(source, station_number, time, variables):

    filepath = sonde_filepath(source)
    filename = sonde_filename(source, station_number, time)

    return iris.load(filepath + filename, variables)


def cubelist_to_dictionary(cubelist):

    sonde_dictionary = {}

    for cube in cubelist:

        name = cube.long_name
