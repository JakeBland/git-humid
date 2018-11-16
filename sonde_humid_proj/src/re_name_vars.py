"""
Collection of functions to convert between the names used for variables in 
files of sonde & ECMWF data and standard names
"""

from collections import defaultdict

def CF_to_source_dict():
    """
    :return: Two dimensional dictionary whose first key is the data source, second key is the name of a variable according
    to the CF standard naming conventions, and which gives the name of a variable according to that data source
    """
    var_names = [['CF_standard_name', 'UKMO', 'sonde', 'ECAN'],
    ['air_pressure', 'air_pressure', 'pressure', 'P'], # ECAN 'P' in hPa where others are in Pa
    ['air_potential_temperature', 'air_potential_temperature', None, None],
    ['mass_fraction_of_cloud_ice_in_air', 'mass_fraction_of_cloud_ice_in_air', None, 'CIWC'],
    ['mass_fraction_of_cloud_liquid_water_in_air', 'mass_fraction_of_cloud_liquid_water_in_air', None, 'CLWC'],
    ['specific_humidity', 'specific_humidity', None, 'Q'], # ECAN 'Q' in g/kg where others are in kg/kg
    ['x_wind', 'x_wind', None, 'U'],
    ['y_wind', 'y_wind', None, 'V'],
    ['time', None, 'time', None],
    ['altitude','altitude','nonCoordinateGeopotentialHeight', 'Z'],
    ['air_temperature', None, 'airTemperature', 'T'],
    ['wind_speed', None,'windSpeed', None],
    ['wind_to_direction', None, 'windDirection', None],
    ['latitude', None, 'latitudeDisplacement', None],
    ['longitude', None, 'longitudeDisplacement', None],
    ['upward_air_velocity', None, None, 'OMEGA'],
    [None, None, None, None]]
    # names of all used variables, None indicating not used
    
    names_dict = defaultdict(dict)
    # creates a dictionary of dictionaries
    
    for a, source in enumerate(var_names[0][1:]):
        for b, variable in enumerate(var_names[1:]):
            names_dict[source][variable[0]] = var_names[b+1][a+1]
            
    return names_dict
    
def source_to_CF_dict():
    """
    :return: Two dimensional dictionary whose first key is the data source, second key is the name of a variable according
    to that data source, and which gives the name of a variable according to the CF standard naming conventions
    """
    var_names = [['CF_standard_name', 'UKMO', 'sonde', 'ECAN'],
    ['air_pressure', 'air_pressure','pressure', 'P'], # ECAN 'P' in hPa where others are in Pa
    ['air_potential_temperature', 'air_potential_temperature',None, None],
    ['mass_fraction_of_cloud_ice_in_air', 'mass_fraction_of_cloud_ice_in_air',None, 'CIWC'],
    ['mass_fraction_of_cloud_liquid_water_in_air', 'mass_fraction_of_cloud_liquid_water_in_air',None, 'CLWC'],
    ['specific_humidity', 'specific_humidity',None, 'Q'], # ECAN 'Q' in g/kg where others are in kg/kg
    ['x_wind', 'x_wind',None, 'U'],
    ['y_wind', 'y_wind',None, 'V'],
    ['time', None, 'time', None],
    ['altitude','altitude','nonCoordinateGeopotentialHeight', 'Z'],
    ['air_temperature', None, 'airTemperature', 'T'],
    ['wind_speed', None,'windSpeed', None],
    ['wind_to_direction', None,'windDirection', None],
    ['latitude', None,'latitudeDisplacement', None],
    ['longitude', None,'longitudeDisplacement', None],
    ['upward_air_velocity', None, None, 'OMEGA'],
    [None, None, None, None]]
    # names of all used variables, None indicating not used
    
    names_dict = defaultdict(dict)
    # creates a dictionary of dictionaries
    
    for a, source in enumerate(var_names[0][1:]):
        for b, variable in enumerate(var_names[1:]):
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
    
    cubelist = cubelist_original.copy()
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
        
        
    