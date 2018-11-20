"""
Collection of functions to re-grid data to specified uniform height scale
"""

import iris
from scipy.interpolate import interp1d

def re_grid_1d(variables, dimension, lower, upper, spacing, kind = 'linear'):
    """
    Take a set of variables defined along a dimension and re-grid them to a uniform scale
    :param variables: list of cubes for the variables
    :param dimension: cube of previous dimension: monotonic and of the same length as variables
    :param lower: number, lower bound of uniform scale
    :param upper: number, upper bound of uniform scale
    :param spacing: number, spacing of uniform scale
    :param kind: integer specifying the order of the spline interpolator to use, default is linear
    :return: list of cubes of new variables
    """
    new_dimension = range(lower, upper+1, int(spacing))
    # create evenly spaced array for new dimension

    new_dim = iris.coords.DimCoord(new_dimension, standard_name = dimension.standard_name, units = dimension.units)

    lat = variables[0].coord('latitude')
    lon = variables[0].coord('longitude')
    time = variables[0].coord('time')
    # read coords of lat, lon & time from the first variable (as they should all be the same)

    new_cubes = iris.cube.CubeList([])

    for cube in variables:

        if cube.shape == (1,) or cube.shape == ():
            # these cubes do not have dimension
            new_cubes.append(cube)
            # just add them to new cube
        else:

            interp_2_new_dim = interp1d(dimension.data, cube.data, kind, bounds_error = False)
            new_data = interp_2_new_dim(new_dimension)
            # interpolate to new dimension array

            new_cubes.append(iris.cube.Cube(new_data, standard_name=cube.standard_name, long_name=cube.long_name,
                                  var_name=cube.var_name, units=cube.units, attributes=cube.attributes,
                                  dim_coords_and_dims=[(new_dim, 0)], aux_coords_and_dims=[(lat,None), (lon,None), (time,None)]))
             # create cube of new interpolated variable on new dimcoord and append to list

    return new_cubes