from types import WrapperDescriptorType
import functions as fx


file = input('Filepath: ')
atom = input('Atom to track: ')
timer = False
timestart = 0
timestop = 0
timestep = float(input('Timestep: '))
timeranged = input('Calculate on range of time? (y/n): ')
if(timeranged == 'y'):
    timer = True
    timestart = float(input('Start time: '))
    timestop = float(input('End time: '))

ranged = False
range = input('Calculate on range of values? (y/n):')

mins = []
maxs = []
directions = []

if(range == 'y'):
    ranged = True
    finished = False
    while(not finished):
        direction = input('Direction? (x,y,z) (n to finish inputting directions): ')
        if(direction == 'n'):
            finished = True
        else:
            directions.append(direction)
            mins.append(float(input('Minimum ' + direction + ' value: ')))
            maxs.append(float(input('Maximum ' + direction + ' value: ')))

vel_dir = input('How many directions to calculate velocity for? (1 or 2): ')
velocity_directions = []
if(vel_dir == '1'):
    vel_dir1 = input('Direction? (x,y,z): ')
    velocity_directions.append(vel_dir1)
elif(vel_dir == '2'):
    vel_dir1 = input('Direction 1? (x,y,z): ')
    vel_dir2 = input('Direction 2? (x,y,z): ')
    velocity_directions.append(vel_dir1)
    velocity_directions.append(vel_dir2)

graph_dir = input('How many directions to graph velocity in? (1 or 2): ')
graph_directions = []
if(graph_dir == '1'):
    graph_dir1 = input('Direction? (x,y,z): ')
    graph_directions.append(graph_dir1)
    xlabel = input('X Label: ')
    ylabel = input('Y Label: ')
elif(graph_dir == '2'):
    graph_dir1 = input('Direction 1? (x,y,z): ')
    graph_dir2 = input('Direction 2? (x,y,z): ')
    graph_directions.append(graph_dir1)
    graph_directions.append(graph_dir2)

else:
    ranged,xmin,xmax = False,0,0

title = input('Graph title: ')


write = input('Write velocities to file? (y/n): ')

if(write == 'y'):
    write_to_file = True
    filename = input('Filename: ')
else:
    filename = ''
    write_to_file = False


print('\n\n')
positions = (fx.read_data(file,atom,'z',timer,timestart,timestop))
coordinates,velocities = fx.calculate_velocities(positions,timestep,ranged,velocity_directions,graph_directions,directions,mins,maxs,write_to_file,filename)
if(graph_dir == '1'):
    fx.graph_with_data_one_direction(coordinates,velocities,xlabel,ylabel,title,'')
elif(graph_dir == '2'):
    fx.graph_with_data_two_directions(coordinates,velocities,title,graph_directions,directions,mins,maxs)