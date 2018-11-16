
iris.FUTURE.cell_datetime_objects=True
import iris
import numpy as np
import datetime

def sonde_filepath(source):
    """
    Define the path to the radiosonde data in this particular case
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :return: file path
    """
    return '/home/users/pr902839/datasets/nawdex/radiosondes/' + source + '/netcdf/'


def model_filepath(model):
    """
    Define path to model data in this particular case
    :param model: Code representing model, options for which are: 'UKMO', 'ECAN'
    :return:
    """
    return '/home/users/pr902839/datasets/nawdex/radiosondes/' + model + '/'


def def_filename(source, station_number, time):
    """
    For given time and location of ascent, return name of the file as structured for this particular case
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :return: file name
    """
    return source + '_' + station_number + '_' + time.strftime('%Y%m%d_%H%M') + '*.nc'
    
    
def UKMO_pressure_double_fix(cubelist):
    """
    UKMO files contain two pressure variables, one of which is on 51 levels, the same as theta, humidity and cloud water
    This function extracts only cubes on these levels, meaning there is a unique pressure variable in the cube list
    :param cubelist: CubeList of UKMO model data
    :return: CubeList of UKMO model data containing only those cubes on 51 vertical levels
    """
    return cubelist.extract(iris.Constraint(cube_func=lambda cube: cube.coord('altitude').shape == (51,)))


def select_lead_time(cubelist, time, lead_time):
    """
    
    :param cubelist:
    :param time:
    :param lead_time:
    :return:
    """
    t = np.mod(time.hour, 6)
    # hours after one of the 6-hourly verification times, 00, 06, 12 or 18 UTC
    ver_time = time + datetime.timedelta(minutes = ((3-np.abs(t-3))*np.sign(t-2.5)*60-time.minute))
    # create second datetime object rounded to the nearest verification time
    # subtracts minutes then subtracts (t<3) or adds (t>=3) hours to nearest 6
    # if this doesn't make sense to you get a pen & paper and work it out          
    start_time = ver_time - datetime.timedelta(days = lead_time)
    # time forecast should be initialised to give appropriate lead time at verification time
    time_constraint = iris.Constraint(forecast_reference_time = start_time)

    new_list = []
    for cube in cubelist:
        new_list.append(cube.extract(time_constraint))
    return iris.cube.CubeList(new_list)


def read_data(source, station_number, time, variables, model = None, lead_time = 0):
    """
    Load the data for a single radiosonde ascent
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param variables: an array containing the variables one wishes to extract from the file, see options in file header
    :param model: to read sonde data leave model = None, to read model data options are: 'UKMO', 'ECAN'
    :param lead_time: time in days before the verification time that the forecast was started
    :return: a cubelist containing the specified variables
    """
    if model == None:
        
        filepath = sonde_filepath(source)
        
    else:
        
        filepath = model_filepath(model)
        
    filename = def_filename(source, station_number, time)

    cubelist = iris.load(filepath + filename, variables)

    if model == 'UKMO':

        cubelist = UKMO_pressure_double_fix(cubelist)
        # This line is necessary, as the files contain two cubes of air_pressure
        # we desire the one on the same number of levels as theta and humidity

        cubelist = select_lead_time(cubelist, lead_time)
        
    return cubelist