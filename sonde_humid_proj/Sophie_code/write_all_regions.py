# taken from Sophie's stuff and put here to compare filter effectiveness

import numpy as np
import os
import math as math
import datetime as datetime

#def split_stations(data):
#    stations = []
#    currentstation = []
#    for column in range(len(data)):
#        currentstation += [[]]
#    for columnno in range(len(data)):
#        currentstation[columnno] += [data[columnno][0]]
#    for lineno in range(1,len(data[0])):
#        if data[0][lineno] != data[0][lineno-1]:
#            stations += [currentstation]
#            currentstation = []
#            for column in range(len(data)):
#                currentstation += [[]]
#        for columnno in range(len(data)):
#            currentstation[columnno] += [data[columnno][lineno]]
#    stations += [currentstation]
#    return stations

def split_stations(sids,data):
    #Splits an array with columns Station ID, Pressure (Pa), Temperature (K), Dew Point Depression (K),
    #Height (m), Longitude, Latitude, Time (s) into a list of arrays of the same form but without
    #Station ID, split according to the stations in the list 'sids'.

    #Prepare list of arrays to contain data
    splitdata = []
    for station in sids:
        splitdata += [[[],[],[],[],[],[],[]]]

    #Extract data for each station, discarding points with recorded temperature < 0K (assumed missing)
    #and converting pressure to hPa, height to km
    for i in range(len(data[0])):
        if data[0][i] in sids and data[2][i] >= 0:
            location = sids.index(data[0][i])
            splitdata[location][0] += [data[1][i]/100.0]
            splitdata[location][1] += [data[2][i]]
            splitdata[location][2] += [data[3][i]]
            splitdata[location][3] += [data[4][i]/1000.0]
            splitdata[location][4] += [data[5][i]]
            splitdata[location][5] += [data[6][i]]
            splitdata[location][6] += [data[7][i]]
            
    return splitdata

def canadian_split_stations(sids,data):
    #Similar to 'split_stations' but for Canadian stations where missing temperature points need to be
    #kept for later processing.

    #Prepare list of arrays to contain data
    splitdata = []
    for station in sids:
        splitdata += [[[],[],[],[],[],[],[]]]

    #Extract data for each station, discarding points with recorded pressure < 0Pa (assumed missing)
    #and converting pressure to hPa, height to km
    if len(data) > 0:
        for i in range(len(data[0])):
            if data[0][i] in sids and data[1][i] >= 0:
                location = sids.index(data[0][i])
                splitdata[location][0] += [data[1][i]/100.0]
                splitdata[location][1] += [data[2][i]]
                splitdata[location][2] += [data[3][i]]
                splitdata[location][3] += [data[4][i]/1000.0]
                splitdata[location][4] += [data[5][i]]
                splitdata[location][5] += [data[6][i]]
                splitdata[location][6] += [data[7][i]]
                
    return splitdata

def new_height(sondedata):
    #Fills in points in Canadian data where height data is missing but temperature is available by
    #first plotting height against pressure regardless of the presence of temperature data and then
    #interpolating onto the points with temperature data present.
    #
    #'sondedata' is the array produced by 'canadian_split_stations' for some station. An array of the
    #same form is produced as output. 

    #Prepare lists h and T containing height and temperature where available and two lists containing
    #pressure - P for points where temperature available, Pnew where height available
    h = [x for x in sondedata[3] if x >= 0]
    P = [sondedata[0][i] for i in range(len(sondedata[0])) if sondedata[3][i]>=0]
    T = [x for x in sondedata[1] if x >= 0]
    Pnew = [sondedata[0][i] for i in range(len(sondedata[0])) if sondedata[1][i]>=0]

    #Remove points in T and Pnew above the highest point where height data is available
    T = [T[i] for i in range(len(T)) if Pnew[i] >= P[-1]]
    Pnew = [x for x in Pnew if x >= P[-1]]

    #Find new height points by interpolation
    hnew = np.interp([-x for x in Pnew],[-x for x in P],h)

    #Extract points from other variables corresponding to where temperature is known
    Tdep = [sondedata[2][i] for i in range(len(sondedata[2])) if sondedata[1][i]>=0 and sondedata[0][i]>=P[-1]]
    longitude = [sondedata[4][i] for i in range(len(sondedata[4])) if sondedata[1][i]>=0 and sondedata[0][i]>=P[-1]]
    latitude = [sondedata[5][i] for i in range(len(sondedata[5])) if sondedata[1][i]>=0 and sondedata[0][i]>=P[-1]]
    t = [sondedata[6][i] for i in range(len(sondedata[6])) if sondedata[1][i]>=0 and sondedata[0][i]>=P[-1]]
    
    return [Pnew,T,Tdep,hnew,longitude,latitude,t]

def find_tropopause(temperature,height):
    #Finds the location of the tropopause according to the WMO definition. Outputs the index of the
    #point in the list 'height' such that the tropopause is half way between height[index-1] and
    #height[index]. If no tropopause found, returns 0.
    
    tropopause = False
    checklevel = 1

    #Move upwards through points where height recorded
    while checklevel < len(height)-1 and not tropopause:
        #Do nothing until outside of boundary layer
        if height[checklevel] > 2:
            #Check if lapse rate of temperature below cutoff
            lapserate = (temperature[checklevel-1]-temperature[checklevel])/(height[checklevel]-height[checklevel-1])
            if lapserate < 2.0:
                index = checklevel+1
                distance = height[index] - height[checklevel]
                checktropopause = True
                #If so, check average lapserate below cutoff for all points in the two km above
                while index < len(height)-1 and distance < 2.0 and checktropopause:
                    averagerate = (temperature[checklevel] - temperature[index])/distance
                    if averagerate > 2.0:
                        checktropopause = False
                    index += 1
                    distance = height[index] - height[checklevel]
                #If conditions satisfied, return location of tropopause
                if checktropopause == True:
                    tropopause = True
                    return checklevel
        checklevel += 1

    #If no tropopause found, return 0.
    if tropopause == False:
        print "no tropopause found"
        return 0

def trop_height(temperature,height):
    #Calculates tropopause height from the output of find_tropopause
    
    index = find_tropopause(temperature,height)
    if index == 0:
        return 0
    return (height[index-1]+height[index])/2.0

def find_potential_temperature(pressure,temperature):
    #Calculates potential temperature from pressure and temperature

    Theta = [temperature[i]*(pressure[i]/1000.0)**(-2.0/7.0) for i in range(len(pressure))]
    return Theta

def clean_up(sonde):
    #Cuts off data above tropopause to leave less to process when finding regions of reduced stability
    
    trop = find_tropopause(sonde[1],sonde[3])
    for i in range(len(sonde)):
        column = sonde[i]
        column = column[:trop]
        sonde[i] = column
    return sonde

def seek_region(height,Theta,start,ref_gradient):
    #Finds highest point where the top of a region of reduced stability with bottom at height[start]
    #could be, given that no region may contain a 200m subregion where the average gradient of
    #potential temperature wrt height is greater than 2*ref_gradient
    
    validstart = False
    checkstart = start
    checkend = start
    distance = 0

    #find first data point at least 200m above height[start]
    while distance < 0.2 and checkend < len(height)-2:
        checkend += 1
        distance = height[checkend] - height[checkstart]

    #check if gradien of Theta sufficiently low - else there can be no reduced stability regions with
    #this start point
    distance = height[checkend] - height[checkstart]
    Thetachange = Theta[checkend] - Theta[checkstart]
    if Thetachange/distance < 2*ref_gradient:
        validstart = True

    #search for first point above height[start] where gradient is too high 
    if validstart:
        validend = True
        while validend and checkend < len(height)-1:
            if height[checkend] - height[checkstart] < 0.2:
                checkend += 1
            elif height[checkend] - height[checkstart+1] >= 0.2:
                checkstart += 1
            else:
                distance = height[checkend] - height[checkstart]
                Thetachange = Theta[checkend] - Theta[checkstart]
                if Thetachange/distance >= 2*ref_gradient:
                    validend = False
                else:
                    checkend += 1
    else:
         checkend = start

    return checkend

def find_unstable_regions(height,PT,ref_gradient):
    #Finds regions of reduced static stability based on the requirements that the average gradient of
    #potential temperature wrt height must be below ref_gradient within the region and that there must
    #be no 200m or greater subsection of the region with average gradient above 2*ref_gradient
    
    possible_regions = []

    #move up through possible locations for the bottom of a low static stability region
    for start in range(len(height)):
        regions = []
        #find highest possible location of top of region
        if start < len(height) - 1:
            end = seek_region(height,PT,start,ref_gradient)
        else:
            end = start
        distance = height[end] - height[start]
        #move down through possible locations for top of region, checking if average gradient of
        #potential temperature sufficiently low
        while distance >= 0.2 and end > start:
            dTheta = PT[end]-PT[start]
            gradient = dTheta/distance
            #if so, and (if uncommenting requirement) if outside of boundary layer, add region to list
            if gradient < ref_gradient:
                #if height[start] > 3:
                    strength = 4*ref_gradient*distance-dTheta
                    regions += [[True,distance,gradient,strength,start,end]]
            end -= 1
            distance = height[end]-height[start]
        possible_regions += regions
    if possible_regions != []:
        regionsleft = True
    else:
        regionsleft = False
    final_regions = []

    #go through list of all possible regions finding and removing the largest one by one
    while regionsleft:
        addregion = [0,0,0,0,-1,-1]
        regionsleft = False
        #find largest region in list
        for region in possible_regions:
                if region[0]:
                    if region[3] >= addregion[3]:
                        addregion = region
        #add it to final list for output
        if addregion != [0,0,0,0,-1,-1]:
            final_regions += [addregion[1:6]]
        #remove any overlapping regions from the original list
        for index in range(len(possible_regions)):
                if possible_regions[index][0]:
                    regionstart = possible_regions[index][4]
                    regionend = possible_regions[index][5]
                    if addregion[5] >= regionstart and addregion[4] <= regionstart:
                        possible_regions[index][0] = False
                    elif addregion[5] >= regionend and addregion[4] <= regionend:
                        possible_regions[index][0] = False
                    else:
                        regionsleft = True
    return final_regions

def interpolate(sondedata):
    #Interpolates data onto 10m height intervals
    
    h = sondedata[3]
    newdata = []
    newh = range(0,int(100*h[-1])+1)
    newh = [x/100.0 for x in newh]
    for variable in sondedata:
        newdata += [np.interp(newh,h,variable)]
    return newdata

def tenm_weights(d):
    #Calculates weights for a truncated gaussian smoothing with half-width d and points every 10m
    
    weights = [math.exp(-((0.01*i)**2)/(2*d**2)) for i in range(0,int(200*d+1))]
    weights = weights[-1:0:-1]+weights
    total = sum(weights)
    weights = [x/total for x in weights]
    return weights

def smooth_equal_10m_intervals(Theta,d):
    #Smooth potential temperature using a truncated Gaussian assuming points are spaced 10m appart
    
    weights = tenm_weights(d)
    newTheta = []
    for i in range(len(Theta)):
        if i >= int(200*d) and i < len(Theta)-int(200*d):
            weightedvalues = [Theta[i-int(200*d)+j]*weights[j] for j in range(len(weights))]
            newTheta += [sum(weightedvalues)]
        else:
            newweights = weights
            if i >= len(Theta)-int(200*d):
                newweights = newweights[:int(200*d)+len(Theta)-i]
            if i < int(200*d):
                newweights = newweights[int(200*d)-i:]
            total = sum(newweights)
            newweights = [x/total for x in newweights]
            if i < int(200*d):
                weightedvalues = [Theta[j]*newweights[j] for j in range(len(newweights))]
            else:
                weightedvalues = [Theta[i-int(200*d)+j]*newweights[j] for j in range(len(newweights))]
            newTheta += [sum(weightedvalues)]
    return newTheta

def average_tropopause_heights():
    #Reads in mean tropopause height for each station from file and formats it as a dictionary
    
    average = {}
    with open("/glusterfs/scenario/users/tk176953/regions_output/tropopauseheights.txt") as f:
        for line in f:
            (sid, meanheight,medheight) = line.split()
            average[int(sid)] = float(meanheight)
    return average

def read_files(directory):
    #Reads all data files and returns information about the reduced static stability regions

    #a list of stations to find information for
    #All:
    sids = [10771, 11952, 16546, 16080, 16045, 16320, 16245, 4320, 10035, 10184, 1400, 7510, 3005, 3808, 7110, 7645, 1028, 1415, 1010, 1001, 14240, 7145, 6011, 1004, 2365, 11035, 10238, 4270, 10113, 10410, 3354, 1241, 2527, 2185, 4339, 10393, 3918, 14430, 10618, 10868, 2591, 10548, 3238, 10739, 3882, 4360,71917,71924,71081,71909,71802,71600]
    #Canadian:
    #sids = [71917,71924,71081,71909,71802,71600]
    #eumetnet:
    #sids = [10771, 11952, 16546, 16080, 16045, 16320, 16245, 4320, 10035, 10184, 1400, 7510, 3005, 3808, 7110, 7645, 1028, 1415, 1010, 1001, 14240, 7145, 6011, 1004, 2365, 11035, 10238, 4270, 10113, 10410, 3354, 1241, 2527, 2185, 4339, 10393, 3918, 14430, 10618, 10868, 2591, 10548, 3238, 10739, 3882, 4360]

    #a dictionary containing mean tropopause heights for each station
    average = average_tropopause_heights()
    #a list of all files in the specified directory
    allfiles = os.listdir(directory)
    
    allregions = []
    regiondata = []
    regionnumbers = []
    
    for f in allfiles:
        print f
        
        #check whether file contains Canadian data and then read in and split by station appropriately
        if "_ua" in f:
            data = np.loadtxt(directory+f, delimiter=",", usecols=(0,1,4,5,6,8,9,11), unpack=True)
            data = canadian_split_stations(sids,data)
            for i in range(len(data)):
                if len(data[i][0]) > 0:
                    fixedsonde = new_height(data[i])
                    data[i] = fixedsonde
        else:
            data = np.loadtxt(directory+f, delimiter=",", usecols=(0,1,4,5,6,8,9,10), unpack=True)
            data = split_stations(sids,data)

        for sondeindex in range(len(data)):
            if len(data[sondeindex][0]) > 0:
                #for each station in the file extract information about location, time measured, etc.
                sid = sids[sondeindex]
                sonde = data[sondeindex]
                time = [int(f[0:10]),int(sonde[6][0])]
                location = [sonde[5][0],sonde[4][0]]
                #process data to remove variability in results due to resolution
                sonde = interpolate(sonde)
                Theta = find_potential_temperature(sonde[0],sonde[1])
                Theta = smooth_equal_10m_intervals(Theta,0.2)
                #find tropopause height and discard points in stratosphere
                trop = trop_height(sonde[1],sonde[3])
                Theta = Theta[:find_tropopause(sonde[1],sonde[3])]
                P,T,Tdep,h,longitude,latitude,t = clean_up(sonde)
                #find regions of reduced static stability
                regions = find_unstable_regions(h,Theta,1.125)
                #record number of regions found and whether the tropopause is higher than average
                regionnumbers += [[trop>average[sid],len(regions)]]
                #find information about the top,bottom and middle of each region and record it
                for region in regions:
                    r1 = region[3]
                    r2 = region[4]
                    start = [T[r1],Tdep[r1],h[r1],Theta[r1]]
                    end = [T[r2],Tdep[r2],h[r2],Theta[r2]]
                    ###
                    hmid = (h[r2]+h[r1])/2.0
                    Tmid = np.interp([hmid],h,T)
                    Tmid = Tmid[0]
                    Tdepmid = np.interp([hmid],h,Tdep)
                    Tdepmid = Tdepmid[0]
                    Thetamid = np.interp([hmid],h,Theta)
                    Thetamid = Thetamid[0]
                    middle = [Tmid,Tdepmid,hmid,Thetamid]
                    ###
                    regiondata += [[sid,time,location,trop,start,end,middle]]
                    
    return regiondata,regionnumbers

def write_to_file(regiondata,regionnumbers):
    #Writes the information about every low stability region to one file and information about the
    #number of regions for each sonde to a second file
    
    f = open("/glusterfs/scenario/users/tk176953/regions_output/allregions.txt","w")
    for region in regiondata:
        sid,time,location,trop,start,end,middle = region
        data = [int(sid)] + location + time + [trop] + start + end + middle
        f.write("{:05d}\t( {:8.4f}, {:8.4f})\t{:10d}\t{:5d}\t{:6.3f}\t{:6.2f}\t{:6.2f}\t{:6.3f}\t{:6.2f}\t{:6.2f}\t{:6.2f}\t{:6.3f}\t{:6.2f}\t{:6.2f}\t{:6.2f}\t{:6.3f}\t{:6.2f}\n".format(*data))
    f.close()
    f = open("/glusterfs/scenario/users/tk176953/regions_output/numbersofregions.txt","w")
    for sonde in regionnumbers:
        f.write("{:}\t{:2d}\n".format(*sonde))
    f.close()

def main():
    directory = "/glusterfs/scenario/users/tk176953/alldata/"
    regiondata,regionnumbers = read_files(directory)
    write_to_file(regiondata,regionnumbers)

main()
