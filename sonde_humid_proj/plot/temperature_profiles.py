import iris
import iris.plot as iplt
import numpy as np
import matplotlib.pyplot as plt


def temperature_profile_comparison_plot(cubelist, cubelist_reg, cubelist_smooth, kind, filter_dic):
    # function to compare re-gridded and filtered temperature profiles to the original

    temp_const = iris.Constraint(name='air_temperature')
    alt_const = iris.Constraint(name='altitude')
    
    trop_alt = cubelist_smooth.extract(iris.Constraint('tropopause_altitude'))[0].data

    temp = cubelist.extract(temp_const)[0].data
    altitude = cubelist.extract(alt_const)[0].data + trop_alt
#
#    uniform_height_temp = re_grid_1d(temp, altitude, 0, 20001, 10, kind)[0]
#    uniform_height = np.array(range(0, 20001, 10))
#
#    filtered_temp = my_filter(uniform_height_temp.data, filter_dic)

    regular_temp = cubelist_reg.extract(temp_const)[0].data
    regular_alt = cubelist_reg.extract(alt_const)[0].data + trop_alt

    smooth_temp = cubelist_smooth.extract(temp_const)[0].data

    plt.figure(figsize = (15, 10))
    plt.plot(temp, altitude, label='original')
    plt.plot(regular_temp, regular_alt, label='re-grid')
    plt.plot(smooth_temp, regular_alt, label='re-grid + filter')
    plt.plot([min(temp), max(temp)], [trop_alt, trop_alt], label = 'WMO tropopause')
    plt.legend()
    plt.xlabel('temperature, K')
    plt.ylabel('altitude, m')
    plt.title('temperature profile comparison')