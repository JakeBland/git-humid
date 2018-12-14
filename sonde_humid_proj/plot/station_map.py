import iris
import os
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

def station_markers(directory = '/home/users/pr902839/datasets/nawdex/radiosondes/UKMO/'):
    # empty array for coordinate pairs
    coord_array = [[], []]
    # station locations with higher res. data
    two_sec = [['EMN', '02365'], ['EMN', '02527'],
               ['EMN', '03005'], ['EMN', '03238'], ['EMN', '03354'], ['EMN', '03808'],
               ['EMN', '03882'], ['EMN', '03918'], ['EMN', '04270'], ['EMN', '04320'],
               ['EMN', '04339'], ['EMN', '04360'], ['EMN', '06011'], ['EMN', '10035'],
               ['EMN', '10113'], ['EMN', '10184'], ['EMN', '10238'], ['EMN', '10393'],
               ['EMN', '10410'], ['EMN', '10548'], ['EMN', '10618'], ['EMN', '10739'],
               ['EMN', '10771'], ['EMN', '10868'],
               ['DLR', '04018'], ['IMO', '04018'], ['NCAS', '03501']]
    # station locations with lower res. data
    sig_lev = [['EMN', '01001'], ['EMN', '01004'], ['EMN', '01010'],
               ['EMN', '01028'], ['EMN', '01241'], ['EMN', '01400'], ['EMN', '01415'],
               ['EMN', '02185'], ['EMN', '02591'], ['EMN', '07110'], ['EMN', '07145'],
               ['EMN', '07510'], ['EMN', '07645'], ['EMN', '11035'], ['EMN', '11952'],
               ['EMN', '14240'], ['EMN', '14430'], ['EMN', '16045'], ['EMN', '16080'],
               ['EMN', '16245'], ['EMN', '16320'], ['EMN', '16546'], ['EMN', 'ASDE01'],
               ['EMN', 'ASDE03'], ['EMN', 'ASDE04'], ['EMN', 'ASDK01'], ['EMN', 'ASDK02'],
               ['EMN', 'ASDK03'], ['EMN', 'ASES01'], ['EMN', 'ASEU01'], ['EMN', 'ASEU02'],
               ['EMN', 'ASEU03'], ['EMN', 'ASEU04'], ['EMN', 'ASEU06'], ['EMN', 'ASFR1'],
               ['EMN', 'ASFR2'], ['EMN', 'ASFR3'], ['EMN', 'ASFR4'], ['EMN', 'DBLK'],
               ['CAN', '71081'], ['CAN', '71600'], ['CAN', '71802'], ['CAN', '71909'],
               ['CAN', '71917'], ['CAN', '71924']]
    # list of list & marker type
    list_list = [[two_sec, '*'], [sig_lev, 'o']]
    # list of all files
    all_file_list = os.listdir(directory)
    # for each station in list
    plt.figure(figsize = (15, 12))
    m = Basemap(projection='merc',\
            llcrnrlat=20, urcrnrlat=82, \
            llcrnrlon=-120, urcrnrlon=40, \
            resolution='l')
    m.drawcoastlines(linewidth=0.25)
    
    f = open('/home/users/bn826011/PhD/git_humid/sonde_humid_proj/docs/station_list.txt', 'w+')
    f.write('station_code latitude longitude altitude number_of_sondes\r\n')
    
    for j, pair in enumerate(list_list):

        for code in pair[0]:
            # list of all files from that station
            ascents = [i for i in all_file_list if i[:-34] == code[0] + '_' + code[1]]
            # number of ascents from station
            no_ascents = len(ascents)
            # arbitrary cube for metadata
            cube_list = iris.load(directory + ascents[0])
            if cube_list:
                example_cube = cube_list[0]
                # read metadata
                latitude = example_cube.coord('latitude').points[0]
                longitude = example_cube.coord('longitude').points[0]
                altitude = example_cube.coord('surface_altitude').points[0]
                # add to array
                coord_array[j].append([no_ascents, latitude, longitude, altitude])
                # plot point on plot
                #plt.scatter(longitude, latitude, s = (no_ascents/20)**2, c = [altitude/1000], cmap = 'copper', marker = pair[1], label = code[0] + '_' + code[1])
            else:
                print code
                
            f.write(repr(code[0] + '_' + code[1]).rjust(12) + ' ' +
                      '{:06.3f}'.format(round(latitude, 3)) + '   ' +
                      '{:07.3f}'.format(round(longitude, 3)) + '    ' +
                      '{:07.3f}'.format(round(altitude, 3)) + '   ' +
                      repr(no_ascents).rjust(8) + '\r\n')
                            
        ca = np.array(coord_array[j])
        
        latitudes = ca[:, 1]
        longitudes = ca[:, 2]  
        
        x, y = m(longitudes, latitudes)
        
        m.scatter(x, y, s = ca[:, 0], c = [ca[:, 3]/1000], cmap = 'viridis', marker = pair[1], edgecolors = 'face')
    
    f.close()
    
    #plt.gca().coastlines(color = [0, 0, 0])
    cbar = plt.colorbar()
    
    # draw parallels and meridians.
    # label parallels on right and top
    # meridians on bottom and left
    parallels = np.arange(0.,81.,10.)
    # labels = [left,right,top,bottom]
    m.drawparallels(parallels,labels=[True,True,False,False])
    meridians = np.arange(-140.,70.,20.)
    m.drawmeridians(meridians,labels=[False,False,True,True])
    
    cbar.set_label('surface altitude, km', rotation=270)
    plt.title('Position of sonde release sites, size indicates no. of sondes')
    plt.savefig('/home/users/bn826011/PhD/figures/sonde_locations.jpg')
    # save