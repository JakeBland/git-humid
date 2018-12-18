"""
Collection of functions to convert between the names used for variables in 
files of sonde & ECMWF data and standard names
"""

from collections import defaultdict

def var_name_array():
    """
    :return: array of names of variables from the three sources used plus cf standard
    """
    
    name_list = [['CF_standard_name', 'UKMO', 'sonde', 'ECAN'],
    ['air_pressure', 'air_pressure', 'pressure', 'P'], # ECAN 'P' in hPa where others are in Pa
    ['air_potential_temperature', 'air_potential_temperature', 'empty', 'empty'],
    ['mass_fraction_of_cloud_ice_in_air', 'mass_fraction_of_cloud_ice_in_air', 'empty', 'CIWC'],
    ['mass_fraction_of_cloud_liquid_water_in_air', 'mass_fraction_of_cloud_liquid_water_in_air', 'empty', 'CLWC'],
    ['specific_humidity', 'specific_humidity', 'empty', 'Q'], # ECAN 'Q' in g/kg where others are in kg/kg
    ['x_wind', 'x_wind', 'empty', 'U'],
    ['y_wind', 'y_wind', 'empty', 'V'],
    ['time', 'empty', 'time', 'empty'],
    ['altitude','altitude','nonCoordinateGeopotentialHeight', 'Z'],
    ['air_temperature', 'empty', 'airTemperature', 'T'],
    ['dew_point_temperature', 'empty', 'dewpointTemperature', 'empty'],
    ['wind_speed', 'empty','windSpeed', 'empty'],
    ['wind_to_direction', 'empty', 'windDirection', 'empty'],
    ['latitude', 'latitude', 'latitudeDisplacement', 'latitude'],
    ['longitude', 'longitude', 'longitudeDisplacement', 'longitude'],
    ['upward_air_velocity', 'empty', 'empty', 'OMEGA'],
    [None, None, None, None]]
    # names of all used variables, 'empty' indicating not used

    for n in range(3):

        name_list[-1][n+1] = [x[n] for x in name_list[1:-1]]
        # such that if user enters 'None', what is returned are all used variables for given source

    return name_list

def CF_to_source_dict():
    """
    :return: Two dimensional dictionary whose first key is the data source, 
    second key is the name of a variable according to the CF standard naming 
    conventions, and which gives the name of a variable according to that data source
    """
    var_names = var_name_array()
    
    names_dict = defaultdict(dict)
    # creates a dictionary of dictionaries
    
    for a, source in enumerate(var_names[0][1:]):
        for b, variable in enumerate(var_names[1:-1]):
            # the '-1' is required to ignore the last line for the 'None' eventuality
            names_dict[source][variable[0]] = var_names[b+1][a+1]
            
    return names_dict
    
def source_to_CF_dict():
    """
    :return: Two dimensional dictionary whose first key is the data source, 
    second key is the name of a variable according to that data source, 
    and which gives the name of a variable according to the CF standard naming conventions
    """
    var_names = var_name_array()
    
    names_dict = defaultdict(dict)
    # creates a dictionary of dictionaries
    
    for a, source in enumerate(var_names[0][1:]):
        for b, variable in enumerate(var_names[1:-1]):
            # the '-1' is required to ignore the last line for the 'None' eventuality
            names_dict[source][var_names[b+1][a+1]] = variable[0]
            
    return names_dict
    
    
def re_name_to_CF(cubelist_original, source):
    """
    Re-names all cubes in a cube list according to CF standard naming conventions
    :param cubelist_original: list of cubes
    :param source: origin of those cubes, either 'UKMO', 'ECAN' or sonde
    :return: cubelist with changed cube names
    """
    CF_lookup = source_to_CF_dict()
    
    cubelist = cubelist_original
    #cubelist = cubelist_original.copy()
    #in order to be well behaved and not modify an input within a function
    
    for cube in cubelist:
        cube.standard_name = CF_lookup[source][str(cube.name())]
        # needs to be changed to a string to get rid of the u at the front
        
    return cubelist
    

def change_names_from_CF(cf_variables, source):
    """
    :param cf_variables: list of strings which are CF standard names
    :param source: source of file whose naming convention you want to change to
    :return: list of strings with naming conventions of source
    """
    CF_lookup = CF_to_source_dict()
    variables = []
    
    for variable in cf_variables:
        
        variables.append(CF_lookup[source][variable])
        
    return variables
        
        
    