import iris
import numpy as np

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


