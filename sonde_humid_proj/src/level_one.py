


def process_single_sonde(time, station_number):
    """
    File to return dictionary of variables derived from sonde data
    :param time: date and time of radiosonde ascent
    :param st_no: station number
    :return: dictionary of altitude, temperature, pressure and specific humidity
    """

    sonde = read_sonde_data(time, st_no, filepath, )