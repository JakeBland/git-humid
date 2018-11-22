"""
Collection of functions to carry out necessary calculations of meteorological values
"""

import numpy as np

import matplotlib.pyplot as plt

def temp_from_theta(theta, pressure, R = 8.31446, cp = 29.07):
    """
    Calculate air_temperature from potential temperature and pressure
    :param theta: array of potential temperature
    :param pressure: corresponding array of pressure
    :param R: gas constant
    :param cp: approximation to isobaric specific heat capacity of air
    :return: array of temperature
    """
    return theta*((pressure/1e5)**(R/cp))

def theta_from_temp(temperature, pressure, R = 8.31446, cp = 29.07):
    """
    Calculate potential temperature from temperature and pressure
    :param temperature: array of temperature
    :param pressure: corresponding array of pressure
    :param R: gas constant
    :param cp: approximation to isobaric specific heat capacity of air
    :return: array of potential temperature
    """
    return temperature*((pressure/1e5)**(-R/cp))

def tropopause_height(T, Z, flag):
    """
    Calculate the tropopause height by WMO definition
    :param T: array of temperature (K)
    :param Z: corresponding array of altitude (m) (assumed to be uniform in vertical for the 2km mean)
    :param flag:
    :return: Tropopause height (number, in metres), and optionally also the array of lapse rate (K/km)
    """
    Z2 = Z[1:-1]
    
    Gamma = 1e3*(T[:-2] - T[2:])/(Z[2:] - Z[:-2])
    
    for index in np.nonzero((Gamma <= 2) * (Z2 >= 5000) * (Z2 <= 22000))[0]:
        # for all individual points at which the lapse rate is less than 2 K/km, between 5km & 22km (Xian 2018) 

        if Z2[-1] < Z2[index] + 2e3:
            index_2 = -1
            flag = 1
            # if there is no point 2km above current, take the highest available
        else:
            index_2 = np.nonzero((Z2 >= Z2[index] + 2e3))[0][0]
            # the index of the lowest point at least 2km above the current point
        
        #if np.average(Gamma[index:index_2+1], weights = (Z[index+2:index_2+3] - Z[index:index_2+1])/2) <= 2:
        # this doesn't work with nans
        weights = (Z[index+2:index_2+3] - Z[index:index_2+1])/2
        weights = weights/sum(weights)
        if np.nanmean(Gamma[index:index_2+1]*weights) <= 2:
            # if the average lapse rate between these layers is also less than 2 K/km
            return Z2[index], flag, Gamma
            
    flag = 2       
    return np.nan, flag, Gamma
    # if there are no layers which satisfy the condition in the profile, return nan
    
