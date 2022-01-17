from matplotlib.legend import Legend
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
import pandas as pd
import numpy as np
from pandas.core import frame
import seaborn as sns
from seaborn.utils import percentiles

#function to read data from trajectory file
def read_data(file_path,molecule,direction,timeranged,timestart,timestop):

    #open the file
    with open(file_path) as file:
        positions = []
        position_append = []
        lines = file.readlines()
        
        i = 0
        at_start = False
        at_end = False
        frame_marker = lines[0][:9]
        if(timeranged):
            while(i < len(lines) and not at_start):
                if(lines[i][:9] == frame_marker):
                    start = lines[i].index('t=')

                    while(not lines[i][start].isdigit() and not lines[i][start] == '.'):
                        start += 1
                    end = start
                    while(lines[i][end].isdigit() or lines[i][end] == '.'):
                        end += 1
                    time = float(lines[i][start:end])
                    if(time >= timestart):
                        at_start = True

                i += 1
            i += 1
        
        while(i < len(lines) and not at_end):

            #checks if the line is a header for a new frame and if so, skips it
            if(lines[i][:9] == frame_marker):
            
                start = lines[i].index('t=')

                while(not lines[i][start].isdigit() and not lines[i][start] == '.'):
                    start += 1
                end = start
                while(lines[i][end].isdigit() or lines[i][end] == '.'):
                    end += 1
                time = float(lines[i][start:end])
                
                if(time >= timestop and timeranged):
                    at_end = True

                #adds the list of coordinates for the previous frame to the
                #master positions list
                if(not i == 0):
                    positions.append(position_append)
                    position_append = []
                i += 1
            else:
                molecule_pos = 9
                #print('i: ' + str(i))
                while(lines[i][molecule_pos] == ' '):
                    molecule_pos += 1
                    #print('pos: ' + str(molecule_pos))

                #checks if line contains the desired molecule
                if(lines[i][molecule_pos:molecule_pos+len(molecule)] == molecule):
                    
                    #starting position of coordinates in line
                    place = 20

                    #get x coordinate
                    x = ''
                    x_found = False
                    x_started = False
                    while(not x_found):
                        if(lines[i][place].isdigit() or lines[i][place] == '.'):
                            x_started = True
                            x += lines[i][place]
                        elif(x_started and not lines[i][place].isdigit()):
                            x_found = True
                        place += 1

                    #get y coordinate
                    y = ''
                    y_found = False
                    y_started = False
                    while(not y_found):
                        if(lines[i][place].isdigit() or lines[i][place] == '.'):
                            y_started = True
                            y += lines[i][place]
                        elif(y_started and not lines[i][place].isdigit()):
                            y_found = True
                        place += 1

                    #get z coordinate
                    z = ''
                    z_found = False
                    z_started = False
                    while(not z_found):
                        if(lines[i][place].isdigit() or lines[i][place] == '.'):
                            z_started = True
                            z += lines[i][place]
                        elif(z_started and not lines[i][place].isdigit()):
                            z_found = True
                        place += 1

                    #add the set of x,y,z to the list of coordinates for the frame
                    position_append.append([float(x),float(y),float(z)])

                #print progress through the file
                percentage = i/len(lines)
                print_percentage(percentage,'Reading data from file: ')
            i += 1

        #add the last set of positions to the master list and return it
        positions.append(position_append)
        print_percentage(1.000,'Reading data from file: ')
        return positions


#function to calculate the velocities given the positions
def calculate_velocities(positions,timestep,ranged,velocity_directions,graph_directions,directions,mins,maxs,write_to_file,filename):

    #set up lists for the coordinates, corresponding velocities, and amount
    #of velocities for a specific coordinate so the average can be calculated
    coordinates = []
    corresponding_velocities = []
    amounts = []

    #set graph_ids based on desired directions
    graph_dir = []
    for direction in graph_directions:
        if(direction == 'x'):
            graph_dir.append(0)
        elif(direction == 'y'):
            graph_dir.append(1)
        elif(direction == 'z'):
            graph_dir.append(2)

    #set velocity_ids based on desired directions
    vel_dir = []
    for direction in velocity_directions:
        if(direction == 'x'):
            vel_dir.append(0)
        elif(direction == 'y'):
            vel_dir.append(1)
        elif(direction == 'z'):
            vel_dir.append(2)

    #set coord_ids based on directions
    dir = []
    for direction in directions:
        if(direction == 'x'):
            dir.append(0)
        elif(direction == 'y'):
            dir.append(1)
        elif(direction == 'z'):
            dir.append(2)

    #x is index in list of positions
    x = 0

    #iterate through the list starting at the second element because the previous
    #element needs to be referenced when calculating velocity
    print('\n')
    while(x < len(positions)-1):
        x += 1

        #print progress through the list
        percentage = x/len(positions)
        print_percentage(percentage,'Calculating velocities: ')

        #iterate through coordinates in each frame
        for y in range(len(positions[x])):
            #check if in range for all directions
            in_range = True
            if(ranged):
                for i in range(len(dir)):
                    if(not positions[x][y][dir[i]] > mins[i] or not positions[x][y][dir[i]] < maxs[i]):
                        in_range = False
            coordinate = []

            for i in range(len(graph_dir)):
                coordinate.append(positions[x][y][graph_dir[i]])


            if(not ranged or in_range):
                if(coordinates.count(coordinate) == 0):
                    coordinates.append(coordinate)

                    #calculate the difference in position
                    dist = 0
                    for i in range(len(vel_dir)):
                        dist += abs(positions[x][y][vel_dir[i]]-positions[x-1][y][vel_dir[i]])**2
                    dist = dist**0.5

                    corresponding_velocities.append(dist)

                    #add 1 to the list of amounts to start a counter for how many times
                    #a difference in position is added for a certain coordinate
                    amounts.append(1)
                            
                else:

                    #if z coordinate already in the list of coordinates get its position
                    #and add the change in position to the corresponding change of position list item
                    #and add one to the amounts to tally how many times a change of positions has
                    #been added
                    idx = coordinates.index(coordinate)

                    dist = 0
                    for i in range(len(vel_dir)):
                        dist += abs(positions[x][y][vel_dir[i]]-positions[x-1][y][vel_dir[i]])**2
                    dist = dist**0.5
                            
                    corresponding_velocities[idx] += dist

                    amounts[idx] += 1

    print_percentage(1.000,'Calculating velocities: ')
    #for each item in the corresponding_velocities, divide by amount of times
    #it was added to to calculate average change in position then divide by timestep
    #to calculate average speed
    print('\n')
    for i in range(len(corresponding_velocities)):
        corresponding_velocities[i] /= amounts[i]
        corresponding_velocities[i] /= timestep
        percentage = i/len(corresponding_velocities)
        print_percentage(percentage,'Averaging velocities: ')
        
    #if the write_to_file option is chosen, will write to the desired filename a list of
    #z coordinates and their corresponding average speeds
    if(write_to_file):
        if(len(graph_directions) == 1):
            writer = graph_directions[0] + '     Velocity\n'
            for i in range(len(coordinates)):
                string =  '{:<6}{:>6}\n'.format(coordinates[i][0],corresponding_velocities[i])
                writer += string

        else:
            writer = graph_directions[0] + '     ' + graph_directions[1] + '     Velocity\n'
            for i in range(len(coordinates)):
                string =  '{:<6}{:<6}{:>6}\n'.format(coordinates[i][0],coordinates[i][1],corresponding_velocities[i])
                writer += string


        output = open(filename,"x")
        output.write(writer)
        output.close()

    return coordinates,corresponding_velocities

    
#graphing function
def graph_with_data_one_direction(coordinates,velocities,x_label,y_label,title,legend):

    coords = []
    for coord in coordinates:
        coords.append(coord[0])
    max_vel = velocities[0]
    for velocity in velocities:
        if(velocity > max_vel):
            max_vel = velocity

    plt.scatter(coords,velocities)
        
    plt.title(title,fontsize=25)
    plt.ylim(0,max_vel*1.1)
    #plt.xlim(0,1)
    plt.xlabel(x_label,fontsize=20)
    plt.ylabel(y_label,fontsize=20)
    #plt.legend(handles=[mpatches.Patch(color='Blue',label=legend)])
    plt.show()

#function to display 2d heatmap of velocities
def graph_with_data_two_directions(coordinates,velocities,title,graph_directions,directions,mins,maxs):
    print('\n')
    x = []
    y = []


    for coordinate in coordinates:
        x.append(coordinate[0])
        y.append(coordinate[1])

    
    xmin = x[0]
    xmax = x[0]
    ymin = y[0]
    ymax = y[0]
    for i in range(len(x)):
        if(x[i] > xmax):
            xmax = x[i]
        if(x[i] < xmin):
            xmin = x[i]
        if(y[i] > ymax):
            ymax = y[i]
        if(y[i] < ymin):
            ymin = y[i]

    xsize = xmax-xmin
    ysize = ymax-ymin
    xgraphmin,xgraphmax = xmin,xmax
    ygraphmin,ygraphmax = ymin,ymax
    grouping = 0.005

    if(xsize > ysize):
        size = math.ceil(xsize/grouping)
    else:
        size = math.ceil(ysize/grouping)

    x_new = []
    y_new = []
    new_velocities = [0]*(size**2)
    counter = [0]*(size**2)

    #set up arrays of grouped coordinates
    for i in range(size):
        for j in range(size):
            x_new.append(round(xmin + (i*grouping),3))
            y_new.append(round(ymin + (j*grouping),3))

    for direction in directions:
        if(not graph_directions.count(direction) == 0):
            if(graph_directions.index(direction) == 0):
                xgraphmin = mins[directions.index(direction)]
                xgraphmax = maxs[directions.index(direction)]
            elif(graph_directions.index(direction) == 1):
                ygraphmin = mins[directions.index(direction)]
                ygraphmax = maxs[directions.index(direction)]

    for i in range(len(x)):
        percentage = i/len(x)
        print_percentage(percentage,'Setting up heat array: ')
        x_val = x[i]
        y_val = y[i]
        x_val -= xmin
        y_val -= ymin
        x_val = math.floor(x_val/grouping)
        y_val = math.floor(y_val/grouping)

        new_velocities[(x_val*size)+y_val] += velocities[i]
        counter[(x_val*size)+y_val] += 1

    print('\n')

    for i in range(len(new_velocities)):
        percentage = i/len(new_velocities)
        print_percentage(percentage,'Averaging new velocities: ')
        if(not counter[i] == 0):
            new_velocities[i] /= counter[i]

    print('\n')
    popped = 0
    counter = 0
    original_length = len(x_new)
    for i in range(len(x_new)-1):
        i -= popped  
        percentage = (i+popped)/original_length
        print_percentage(percentage,'Clearing zero velocities: ')
        
        if(new_velocities[i] == 0):
            popped += 1
            x_new.pop(i)
            y_new.pop(i)
            new_velocities.pop(i)



    print('\n')
    print(len(x_new))
    popped = 0
    for i in range(len(x_new)-1):
        i -= popped
        percentage = i/len(x_new)
        print_percentage(percentage,'Clearing outliers: ')
        
        if(x_new[i] < xgraphmin or x_new[i] > xgraphmax or y_new[i] < ygraphmin or y_new[i] > ygraphmax):
            popped += 1
            x_new.pop(i)
            y_new.pop(i)
            new_velocities.pop(i)




    print_percentage(1.00,'Clearing outliers: ')



    xaxis = graph_directions[0] + ' coordinate'
    yaxis = graph_directions[1] + ' coordinate'

    df = pd.DataFrame.from_dict(np.array([x_new,y_new,new_velocities]).T)
    df.columns = [xaxis,yaxis,'Velocities']
    df['Velocities'] = pd.to_numeric(df['Velocities'])
    
    pivotted= df.pivot(yaxis,xaxis,'Velocities')
    sns.heatmap(pivotted,cmap='rainbow')
    plt.title(title)
    print('x min: ' + str(xgraphmin) + ' xmax: ' + str(xgraphmax))
    print('y min: ' + str(ygraphmin) + ' ymax: ' + str(ygraphmax))

    plt.show()


def print_percentage(percentage,string):
    percentage = round((percentage*100),1)
    print(string + str(percentage) + '%', end='\r')

'''temps = ['20C','40C','60C','75C','90C']
pores = ['bulk','2nm','4nm','6nm','8nm','10nm']
filename = 'nvt_noPBC.xtc'


for temp in temps:
    data = []
    for pore in pores:
        file_path = 'with_temp/' + pore + '/' + temp + '/' + filename'''
