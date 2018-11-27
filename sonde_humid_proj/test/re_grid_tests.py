import iris
import numpy as np

import iris.quickplot as qplt
import matplotlib.pyplot as plt


def test_altitude(cubelist_dictionary):
    """
    Tests that the variable altitude and the coordinate altitude are identical
    :param cubelist_dictionary:
    :return:
    """

    alt_const = iris.Constraint(name = 'altitude')

    for key in cubelist_dictionary:

        cubelist = cubelist_dictionary[key]

        altitude = cubelist.extract(alt_const)[0]

        alt_coord = altitude.coord('altitude')

        assert (np.nonzero(altitude.data - alt_coord.points)[0] == np.nonzero(np.isnan(altitude.data - alt_coord.points))[0]).all(), \
               "altitude variable is not the same as dimension for " + key
        # returns true only if the two arrays are identical at all points where
        # neither has the value 'nan'
        #(in this case, altitude the variable is set to 'nan' below the ground)


def sanity_check(cubelist_dictionary):
    """
    Plot plots of pressure, temperature, RHi and potential temperature
    To make sure things don't differ too wildly
    """
    
    plt.figure(figsize = (12, 8))
    
    for key in cubelist_dictionary:
        
        cubelist = cubelist_dictionary[key]
        
        pressure = cubelist.extract(iris.Constraint(name = 'air_pressure'))[0]
        temperature = cubelist.extract(iris.Constraint(name = 'air_temperature'))[0]
        RHi = cubelist.extract(iris.Constraint(name = 'relative_humidity_ice'))[0]
        theta = cubelist.extract(iris.Constraint(name = 'air_potential_temperature'))[0]
        altitude = cubelist.extract(iris.Constraint(name = 'altitude'))[0]
        
        plt.subplot(2, 2, 1)
        qplt.plot(altitude, pressure)
        plt.subplot(2, 2, 2)
        qplt.plot(altitude, temperature)
        plt.subplot(2, 2, 3)
        qplt.plot(altitude, RHi, label = key)
        plt.subplot(2, 2, 4)
        qplt.plot(altitude, theta)
        
    plt.subplot(2, 2, 3)
    plt.legend()
    