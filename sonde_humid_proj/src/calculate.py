"""
Collection of functions to carry out necessary calculations of meteorological quantities
"""

from __future__ import division
import numpy as np

def gp_to_gph(geopotential, g = 9.80665):
    """
    Calculate geopotential height from geopotential
    :param geopotential: number or array of geopotential in m^2 s-2
    :return: number or array of geopotential height in m
    """
    return geopotential/g

def altitude_from_GPH(geopotential_height, a = 6371229.0):
    """
    Calculate geometric altitude from geopotential height
    :param geopotential_height: array of geopotential height in m
    :param a: radius of the earth
    :return: array of altitude
    """
    return a*geopotential_height/(a-geopotential_height)

def temp_from_theta(theta, pressure, R = 8.31446, cp = 29.07):
    """
    Calculate air_temperature from potential temperature and pressure
    :param theta: array of potential temperature in K
    :param pressure: corresponding array of pressure in Pa
    :param R: gas constant
    :param cp: approximation to isobaric specific heat capacity of air
    :return: array of temperature
    """
    return theta*((pressure/1e5)**(R/cp))

def theta_from_temp(temperature, pressure, R = 8.31446, cp = 29.07):
    """
    Calculate potential temperature from temperature and pressure
    :param temperature: array of temperature in K
    :param pressure: corresponding array of pressure in Pa
    :param R: gas constant
    :param cp: approximation to isobaric specific heat capacity of air
    :return: array of potential temperature
    """
    return temperature*((pressure/1e5)**(-R/cp))

def partial_from_vapour(vapour_pressure, temperature, pressure):
    """
    Calculate partial pressure of water vapour from vapour pressure 
    with respect to liquid water using eq. A4.7 in Gill AOD p606
    :param vapour_pressure: array of vapour pressure with respect to liquid water in Pa
    :param temperature: array of air temperature in K
    :param pressure: array of total air pressure in Pa
    :return: array of partial pressure of water vapour in Pa
    """
    return (1 + 1e-8*pressure*(4.5 + 6e-4*(temperature - 273.15)**2))*vapour_pressure

def q_from_partialpressure(partial_pres, pressure, repsilon = 0.621981):
    """
    Calculate specific humidity from vapour pressure using eq. A4.3 in Gill AOD p606, 
    equiv. 3.1.12 p41, equiv. 5.22 in Ambaum TPOA p100
    :param partial_pres: array of partial pressure of water vapour in Pa
    :param pressure: array of pressure in Pa
    :param repsilon: number, ratio of effective molar masses of water and dry air, approx 0.62198
    :return: array of specific humidity in kg kg-1
    """
    return repsilon*partial_pres/(np.amax([pressure, partial_pres], 0) - 
                                                     (1-repsilon)*partial_pres)
    # using the fix of 'amax(pressure, partial_pres)' means that q is capped at 1kg/kg if for some reason e > p    
    # FIND ACTUAL SOURCE - I think I found this reading through the code for the UM

def vapour_pressure_from_q(q, pressure, repsilon = 0.621981):
    """
    Calculate vapour pressure from specific humidity using eq. A4.3 in Gill AOD p606, 
    equiv. 3.1.12 p41, equiv. 5.22 in Ambaum TPOA p100
    :param q: array of specific humidity in Pa
    :param pressure: array of pressure in Pa
    :param repsilon: number, ratio of effective molar masses of water and dry air, approx 0.62198
    :return: array of vapour pressure in Pa
    """
    return pressure*q/(repsilon + (1-repsilon)*q)

def RH_from_vapourpressure(vapour_pres, temp, state = 'mixed', T0 = 273.16, Ti = 250.16):
    """
    Calculate relative humidity with respect to specified state
    :param vapour_pres: array of vapour pressure in Pa
    :param temp: array of temperature in K
    :param state: state to calculate saturation vapour pressure with respect to, 
                  either 'liquid water', 'ice' or 'mixed'
    :param T0: temperature above which RH is calculated only wrt liquid water in mixed state
    :param Ti: temperature below which RH is calculated only wrt ice in mixed state
    :return: array of relative humidity in kg kg-1
    """

    if state == 'liquid_water':

        svp = svpw_from_temp(temp)

    elif state == 'ice':

        svp = svpi_from_temp(temp)

    elif state == 'mixed':

        svpw = svpw_from_temp(temp)
        svpi = svpi_from_temp(temp)

        A = (temp - Ti)/(T0 - Ti)
        # array indicating relative distance between T0 and Ti
        # A > 1 for temp > T0, A < 0 for temp < Ti, 0 < A < 1 for Ti < temp < T0

        B = np.amax([np.amin([A, np.ones_like(A)], axis = 0), np.zeros_like(A)], axis = 0)
        # adjusts A s.t. B = 1 for temp > T0 and B = 0 for temp < Ti

        svp = svpi + (svpw - svpi)*(B**2)
        # quadratic fit of svp for Ti < temp < T0
        # svp = svpw for temp > T0
        # svp = svpi for temp < Ti

    else:

        print("RH_from_vapourpressure has three options for state for RH to be " +
              "calculated with respect to: \n 'liquid_water', 'ice' or 'mixed'" +
              " \n As you have decided to enter something else, this function will now fail")

    return vapour_pres/svp


def svpw_from_temp(temp):
    """
    Calculate saturation vapour pressure with respect to liquid water from 
    temperature using Sonntag numerical approximation
    :param temp: array of temperature in K
    :return: array of vapour pressure with respect to water in Pa
    """
    return 100*np.exp(-6096.9385/temp
                      + 16.635794
                      - 2.711193e-2*temp
                      + 1.673952e-5*(temp**2)
                      + 2.433502*np.log(temp))

def svpi_from_temp(temp):
    """
    Calculate saturation vapour pressure with respect to ice from temperature 
    using Sonntag numerical approximation
    :param temp: array of temperature in K
    :return: array of vapour pressure with respect to ice in Pa
    """
    return 100*np.exp(-6024.5282/temp
                      + 24.721994
                      + 1.0613868e-2*temp
                      - 1.3198825e-5*(temp**2)
                      - 0.49382577*np.log(temp))

def tropopause_height(T, Z, flag):
    """
    Calculate the tropopause height by WMO definition
    :param T: array of temperature (K)
    :param Z: corresponding array of altitude (m)
    :param flag: number, 0 when things are working well, 
                 and asigned to a number when somthing goes wrong
    :return: Tropopause height (number, in metres), 
             and optionally also the array of lapse rate (K/km)
    """
    Z2 = Z[1:-1]
    
    Gamma = 1e3*(T[:-2] - T[2:])/(Z[2:] - Z[:-2])
    
    for index in np.nonzero((Gamma <= 2) * (Z2 >= 4000) * (Z2 <= 18000))[0]:
        # for all individual points at which the lapse rate is less than 2 K/km, 
        # between 4km & 18km (following Ben Harvey)

        if Z2[-1] < Z2[index] + 2e3:
            index_2 = -1
            flag = 1
            # if there is no point 2km above current, take the highest available and raise flag
        else:
            index_2 = np.nonzero((Z2 >= Z2[index] + 2e3))[0][0]
            # the index of the lowest point at least 2km above the current point
        
        #if np.average(Gamma[index:index_2+1], weights = (Z[index+2:index_2+3] - Z[index:index_2+1])/2) <= 2:
        # this doesn't work with nans
        weights = (Z[index+2:index_2+3] - Z[index:index_2+1])/2
        weights = weights/sum(weights)
        # temperature at each point weighted by the vertical extent it represents
        if np.nansum(Gamma[index:index_2+1]*weights) <= 2:
            # if the average lapse rate between these layers is also less than 2 K/km
            return Z2[index], flag, Gamma
            
    flag = 2
    return np.nan, flag, Gamma
    # if there are no layers which satisfy the condition in the profile, return nan and raise flag



def gradient(v1, v2, v3, c1, c2, c3):
    """
    second order accurate, first derivative of variable v with respect to coordinate c
    vi are values (or arrays thereof) of v at coordinates ci
    the derivative is found at point c2
    the numbering is by convention and there is no requirement for c1 < c2 < c3
    it is however required that none of the ci are equal to each other
    :return: first derivative of v at point c2 in direction of c
    """
    A = ((c3 - c2)/(c1 - c2))
    # this expression can be derived easily using taylor series
    print np.shape((A*v1 + (1/A - A)*v2 - v3/A)/(c3 - c1))
    return (A*v1 + (1/A - A)*v2 - v3/A)/(c3 - c1)

def array_gradient_axis1(var, coord):
    """
    gradient of variable var along coordinate coord
    :param var: array, with at least two dimensions
    :param coord: array, corresponds to the second dimension of var
    :return: array of same shape as var of gradient in direction of coord
    """
    # create empty array to populate with gradient values
    var_grad = np.zeros_like(var)
    # for endpoints use the two nearest points to calculate gradient
    var_grad[:,0] = gradient(var[:,1], var[:,0], var[:,2], coord[:,1], coord[:,0], coord[:,2])
    var_grad[:,-1] = gradient(var[:,-3], var[:,-1], var[:,-2], coord[:,-3], coord[:,-1], coord[:,-2])
    # in the middle calculate gradient using points either side
    var_grad[:,1:-1] = gradient(var[:,:-2], var[:,1:-1], var[:,2:], coord[:,:-2], coord[:, 1:-1], coord[:, 2:])

    return var_grad

def Nsquared_from_thetagrad(theta, theta_grad, g = 9.80665):
    """
    Square of Brunt Vaisala frequency
    :param theta: array of potential temperature
    :param theta_grad: gradient of potential temperature
    :param g: gravitational acceleration, here approximated as a constant
    :return: array of square of brunt vaisala frequency
    """
    return g*theta_grad/theta

def g_update(altitude, a = 6371229.0, g = 9.80665):
    """
    Update g depending on altitude, to reduce with distance from surface
    :param altitude:
    :param a:
    :param g:
    :return:
    """
    return g/(1 + altitude/a)**2


