
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

def tropopause_height(temperature, altitude):


def