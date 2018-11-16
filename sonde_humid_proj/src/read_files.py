
import iris
iris.FUTURE.cell_datetime_objects=True
import numpy as np
import datetime

from re_name_vars import change_names_from_CF, re_name_to_CF

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


def ECAN_pressure_units_fix(cubelist):
    """
    Changes the units of cube of pressure within cubelist if it is there
    :param cubelist: list of cubes
    """
    cube = cubelist.extract(iris.Constraint(name = 'P'))
    if cube:
        cube.convert_units('Pa')
    
   
def ECAN_humidity_units_fix(cubelist):
    """
        Changes the units of cube of hunidity within cubelist if it is there
        :param cubelist: list of cubes
        """
    cube = cubelist.extract(iris.Constraint(name = 'Q'))
    if cube:
        cube.convert_units('kg/kg')


def select_lead_time(cubelist, time, lead_time):
    """
    Take CubeList containing cubes with several forecast reference times and extract desired lead time
    :param cubelist: list of cubes with several forecast lead times
    :param time: datetime object of the time of the release of the sonde
    :param lead_time: time in days before the verification time that the forecast was started
    :return: list of cubes with only desired forecast reference time
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
    
    
def add_ECAN_metadata(filepath, filename, cubelist_original):
    
    cubelist = cubelist_original.copy()
    
    metalist = iris.load(filepath+filename, ['AN_TIME', 'LAT', 'LON'])
    
    T = metalist[0].data
    # list of strings detailing the time of launch
    
    year = int(T[0]+T[1]+T[2]+T[3])
    month = int(T[4]+T[5])
    day = int((T[6]+T[7]))
    hour = int((T[9]+T[10]))
    
    time = datetime.datetime(year, month, day, hour) - datetime.datetime(1970, 1, 1)
    t_hours = time.days*24
    # convert this list of strings into an interpretable object
    
    tm = iris.coords.AuxCoord(t_hours, long_name = 'time', units=Unit('hours since 1970-01-01 00:00:00', calendar='gregorian'))
    lat = iris.coords.AuxCoord(metacube[1].data, long_name = 'Latitude', units = 'degrees_north')
    lon = iris.coords.AuxCoord(metacube[2].data, long_name = 'Longitude', units = 'degrees_east')
    # create coordinates
    
    for cube in cubelist:
        
        cube.add_aux_coord(tm)
        cube.add_aux_coord(lat)
        cube.add_aux_coord(lon)
        
    return cubelist


def read_data(source, station_number, time, cf_variables = None, model = None, lead_time = 0):
    """
    Load the data for a single radiosonde ascent
    :param source: Code representing origin of data, options for which are: 'EMN', 'CAN', 'DLR', 'IMO', 'NCAS'
    :param station_number: 4-6 digit identifier of particular station from which sonde was released
    :param time: datetime object of the time of the release of the sonde
    :param cf_variables: an array containing the CF standard names of variables one wishes to extract from the file
                      if variables == None function will return all variables in file
    :param model: to read sonde data leave model = None, to read model data options are: 'UKMO', 'ECAN'
    :param lead_time: time in days before the verification time that the forecast was started
    :return: CubeList containing the specified variables
    """
    if model == None:
        
        filepath = sonde_filepath(source)
        model = 'sonde'
        # this becomes convenient for specifying the naming convention
        
    else:
        
        filepath = model_filepath(model)
        
    filename = def_filename(source, station_number, time)
    
    variables = change_names_from_CF(cf_variables, model)
    # change the array of names to those names in the source file

    cubelist = iris.load(filepath + filename, variables)

    if model == 'UKMO':

        cubelist = UKMO_pressure_double_fix(cubelist)
        # This line is necessary, as the files contain two cubes of air_pressure
        # we desire the one on the same number of levels as theta and humidity
        cubelist = select_lead_time(cubelist, lead_time)
        
        cubelist.append(make_alt_cube(cubelist[0]))
        # MAKE THIS LINE BETTER
        
    elif model == 'ECAN':
        
        ECAN_pressure_units_fix(cubelist)
        ECAN_humidity_units_fix(cubelist)
        # ensure that the units are uniform from all three data sources
        
        cubelist = add_ECAN_metadata(filepath, filename, cubelist)

    cubelist = re_name_to_CF(cubelist, model)
    # then re-name all the cubes according to CF conventions for uniformity

    return cubelist
    
def make_alt_cube(test_cube):
    # make a cube of altitude from UM data where it is the vertical coordinate
    
    alt = test_cube.copy()
    
    alt_coord = alt.coord('altitude')
    
    alt.data = alt_coord.points
    alt.standard_name = alt_coord.standard_name
    alt.units = alt_coord.units
    alt.var_name = alt_coord.var name
    
    return alt