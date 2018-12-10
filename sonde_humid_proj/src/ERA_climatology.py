
import iris
import iris.analysis
iris.FUTURE.cell_datetime_objects=True
import calculate

import matplotlib.pyplot as plt

def find_mean_trop_GPH(plat, plon):
    """
    Find mean tropopause geopotential height at a given latitude and longitude
    from ERA interim data, at a specified latitude & longitude
    :param plat: number, latitude of desired point
    :param plon: number, longitude of point
    :return: number, mean geopotential height of tropopause
    """
    # load data for geopotential on 2PVU (Sept & Oct from 2005 - 2018)
    #geopotential = iris.load('/home/users/bn826011/PhD/ERA_Interim_tropopause_geopotential/ERA_2005_2018_SepOct.nc')
    geopotential = iris.load('/home/users/bn826011/PhD/ERA_Interim_tropopause_geopotential/ERA_trop_2010.nc')[0]
    # take mean over all months
    gpm = geopotential.collapsed('time', iris.analysis.MEAN)

    #load latitude & longitude coordinates
    lat = gpm.coord('latitude')
    lon = gpm.coord('longitude')

    lon_idx = lon.points[lon.points < plon].argmax()
    # the index of the largest value in the lon array less than desired plon
    lat_idx = lat.points[lat.points < plat].argmax()

    alpha = plat - lat.points[lat_idx]
    beta = plon - lon.points[lon_idx]
    # for linear interpolation

    gp_at_point = ((1 - alpha)*((1 - beta)*gpm.data[lat_idx, lon_idx] + beta*gpm.data[lat_idx, lon_idx+1]) +
                   alpha*((1 - beta)*gpm.data[lat_idx+1, lon_idx] + beta*gpm.data[lat_idx+1, lon_idx+1]))

    # convert geopotential to geopotential height
    return gp_at_point/9.80655