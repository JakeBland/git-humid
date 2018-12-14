import iris
iris.FUTURE.cell_datetime_objects=True
import matplotlib.pyplot as plt

import sys
# Add the parent folder path to the sys.path list
sys.path.append('..')

import src.calculate
from src.ERA_climatology import find_mean_trop_GPH

def compare_trop_heights(station_code):
    """
    Initial comparison between the reference tropopause height calculated from ERA Interim,
    and those calculated by WMO definition from obs & analyses, to inform definition of ridge & trough
    :param station_code: string, first digits of which identify source, and the
                         second digits identify the particular station, e.g. 'EMN_03882'
    """

    sonde_trop = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/'
                           + station_code + '/sonde_2D_trop_relative.nc', 'tropopause_altitude')[0]
    ukmo_trop = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/'
                          + station_code + '/ukmo_2D_trop_relative.nc', 'tropopause_altitude')[0]
    ecan_trop = iris.load('/home/users/bn826011/PhD/radiosonde/NAWDEX_timeseries/high_res/'
                          + station_code + '/ecan_2D_trop_relative.nc', 'tropopause_altitude')[0]
    # load trop_altitude from obs & analyses

    trop_list = [sonde_trop, ukmo_trop, ecan_trop]
    nlist = ['sonde', 'ukmo', 'ecan']

    lat = sonde_trop.coord('latitude').points[0]
    lon = sonde_trop.coord('longitude').points[0]
    # read latitude & longitude of station

    mean_trop_gph = find_mean_trop_GPH(lat, lon)
    # find mean tropopause geopotential at station location
    trop_ref = src.calculate.altitude_from_GPH(mean_trop_gph)
    # convert to altitude

    start_time = sonde_trop.coord('time').points[0]
    end_time = sonde_trop.coord('time').points[-1]
    # first & last times in timeseries

    plt.figure(figsize=(12, 8))

    for n, trop in enumerate(trop_list):
        plt.plot(trop.coord('time').points, trop.data, label=nlist[n])

    plt.plot([start_time, end_time], [trop_ref, trop_ref], label='ERA-Interim Sept/Oct mean')
    # plot tropopause timeseries against reference on same plot to compare
    plt.legend()
    plt.xlabel('time, h')
    plt.ylabel('altitude, m')
    plt.title('Tropopause height from obs & analysis compared to reference for ' + station_code)

    plt.savefig(
        '/home/users/bn826011/PhD/figures/Tropopause_timeseries/' + station_code + '.jpg')