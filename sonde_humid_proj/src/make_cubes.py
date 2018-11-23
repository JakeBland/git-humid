"""
Collection of functions to take as arguments a cubelist, and return cubes of desired variables, calculated using 'calculate'
"""
import iris
import calculate

def temperature_cube(cubelist):
    """
    Create cube of temperature
    :param cubelist: list of cubes containing pressure and theta
    :return: cube of temperature
    """
    theta = cubelist.extract(iris.Constraint(name='air_potential_temperature'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    # [0] required as cubelist.extract returns a cube list

    temp = calculate.temp_from_theta(theta.data, pressure.data)

    temperature = theta.copy()
    temperature.standard_name = 'air_temperature'
    temperature.data = temp

    return temperature


def theta_cube(cubelist):
    """
    Create cube of potential temperature
    :param cubelist: list of cubes containing pressure and tenperature
    :return: cube of potential temperature
    """
    temperature = cubelist.extract(iris.Constraint(name='air_temperature'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    # [0] required as cubelist.extract returns a cube list

    pot_temp = calculate.theta_from_temp(temperature.data, pressure.data)

    theta = temperature.copy()
    theta.standard_name = 'air_potential_temperature'
    theta.data = pot_temp

    return theta


def specific_humidity_cube(cubelist):
    """
    Create cube of specific humidity
    :param cubelist: list of cubes containing dew point temperature, pressure and tenperature
    :return: cube of specific humidity
    """
    dew_point = cubelist.extract(iris.Constraint(name='dew_point_temperature'))[0]
    temperature = cubelist.extract(iris.Constraint(name='air_temperature'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    # [0] required as cubelist.extract returns a cube list

    vapour_pressure = calculate.svpw_from_temp(dew_point.data)
    partial_pressure = calculate.partial_from_vapour(vapour_pressure, temperature.data, pressure.data)
    spec_hum = calculate.q_from_partialpressure(partial_pressure, pressure.data)

    q = dew_point.copy()
    q.standard_name = 'specific_humidity'
    q.units = 'kg kg-1'
    q.data = spec_hum

    return q

def relative_humidity_cube(cubelist, state):
    """
    Create cube of relative humidity with respect to specified state
    :param cubelist: list of cubes containing specific humidity, pressure and tenperature
    :param state: state to calculate saturation vapour pressure with respect to, either 'liquid water', 'ice' or 'mixed'
    :return: cube of relative humidity
    """
    specific_humidity = cubelist.extract(iris.Constraint(name = 'specific_humidity'))[0]
    pressure = cubelist.extract(iris.Constraint(name='air_pressure'))[0]
    temperature = cubelist.extract(iris.Constraint(name='air_temperature'))[0]

    vapour_pres = calculate.vapour_pressure_from_q(specific_humidity.data, pressure.data)
    RH = calculate.RH_from_vapourpressure(vapour_pres, temperature.data, state)

    RHs = specific_humidity.copy()
    RHs.rename('relative_humidity_' + state)
    # the standard name would be 'relative_humidity', but to provide distinction
    RHs.data = RH

    return RHs