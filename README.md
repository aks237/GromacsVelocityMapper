# GromacsVelocityMapper
Project to map the velocity profiles of Gromacs simulation files

This project takes gromacs simulation files that have the coordinates of the molecules in the simulation at each timestep and can calculate the average velocities of certain types of molecules at given coordinates and plot them, thus giving an visual representation of how the molecules tend to be moving in the simulation. The program allows velocity to be calculated in one or two directions and then mapped in one or two directions. When the velocity is mapped in one direction, a 2D plot will be given of the velocities along that direction in the simulation with the direction coordinate on the x axis and the corresponding velocities on the y axis. When the velocity is mapped in two directions, a heatmap will be produced that gives a visual representation of the velocity profile in your simulation, which is very useful when simulating nanopores. The program also allows dimensional restraints to be applied when calculating the molecular velocities.
