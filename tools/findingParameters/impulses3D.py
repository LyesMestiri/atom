import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mayavi.mlab import *
from mayavi import mlab
import reader as rd
import argparse


def impulseToSpeed(impulses) :
	speed = [[], [], []]
	for i in range(len(impulses[0])) :
		gamma = (impulses[0][i]**2 + impulses[1][i]**2 + impulses[2][i]**2 )**0.5
		speed[0] += [impulses[0][i] / gamma]   #!!!! ABS ??
		speed[1] += [impulses[1][i] / gamma]   #!!!! ABS ??
		speed[2] += [impulses[2][i] / gamma]   #!!!! ABS ??
	return speed


# Displays the impulses of the particles with matplotlib
def displayParticles3D(coordinates, impulses, sort, scl=1) :
	h = 1.255/100 #Gap between nodes
	step = 1000 #Display one particle out of 'step'

	# Determining the scale to apply depending on the sort
	scales = [2, 0.75, 2]
	scale = scl*abs(scales[sort]/max(max(impulses[0]), max(impulses[1]), max(impulses[2])))

	# Setting the coordinates and impulses to display
	x = [coordinates[0][i]/h for i in range(0, len(coordinates[0]), step)]
	y = [coordinates[1][i]/h for i in range(0, len(coordinates[1]), step)]
	z = [coordinates[2][i]/h for i in range(0, len(coordinates[2]), step)]
	u = [impulses[0][i]*scale for i in range(0, len(impulses[0]), step)]
	v = [impulses[1][i]*scale for i in range(0, len(impulses[1]), step)]
	w = [impulses[2][i]*scale for i in range(0, len(impulses[2]), step)]

	# Coloring the arrows for each particles
	col = []

	cmax = [max(u), max(v), max(w)]
	cmin = [min(u), min(v), min(w)]

	for i in range(len(u)) :
		# Normalizing
		partColor = [abs((u[i]-cmin[0])/(cmax[0]-cmin[0])), abs((v[i]-cmin[1])/(cmax[1]-cmin[1])), abs((w[i]-cmin[2])/(cmax[2]-cmin[2]))]

		# Finding the most important coordinate
		maxVal = partColor[0]
		maxIndex = 0
		for j in range(1, len(partColor)) :
			if (maxVal<partColor[j]) :
				maxVal = partColor[j]
				maxIndex = i

		# Decrease the importance of other coordinates
		partColor[(maxIndex+1)%3] /= 10
		partColor[(maxIndex+2)%3] /= 10

		# Applying the color
		col = col + [(partColor[0], partColor[1], partColor[2])]

	# Coloring the arrow's head
	for i in range(len(u)) :
		col = col + [col[i], col[i]]

	# Initializing matplotlib figure
	fig = plt.figure("Sort " + str(sort+1))
	ax = fig.add_subplot(111, projection='3d')

	ax.set_xlabel('X axis')
	ax.set_ylabel('Y axis')
	ax.set_zlabel('Z axis')

	ax.set_xlim([0, 102])
	ax.set_ylim([0, 6])
	ax.set_zlim([0, 6])

	ax.tick_params(axis='x', colors='red')
	ax.tick_params(axis='y', colors='green')
	ax.tick_params(axis='z', colors='blue')

	ax.xaxis.label.set_color('red')
	ax.yaxis.label.set_color('green')
	ax.zaxis.label.set_color('blue')

	ax.text2D(0.05, 0.95, "scale : "+str(scale), transform=ax.transAxes)

	# Drawing the particles
	q = ax.quiver(x, y, z, u, v, w, colors = col)


# Displays the impulses of the nodes with mayavi
def displayNodes3D(impulses, sort, scale) :

	# Meshgrid for the positions
	x, y, z = np.meshgrid(np.arange(0, 102, 1),
                      np.arange(0, 6, 1),
                      np.arange(0, 6, 1))

	# Impulses grids
	u = impulses[0]
	v = impulses[1]
	w = impulses[2]

	quiver3d(x, y, z, u, v, w, line_width=2, scale_factor=scale)
	mlab.show()


# Loads the coordinates and impulses for matplotlib display
def runParticles3D(path, sorts, scale, speed=False) :
	for sort in range(len(sorts)) :
		if (sorts[sort]) :
			[coordinates, impulses] = rd.readCoorImp(path, sort)

			if (speed) :
				impulses = impulseToSpeed(impulses)

			displayParticles3D(coordinates, impulses, sort, scale)


# Loads the impulses for mayavi display
def runNodes3D(path, sorts, scl = 1, speed=False) :
	size = (102, 6, 6, 3)
	h = 1.255/100

	for sort in range(len(sorts)) :
		if (sorts[sort]) :
			[coordinates, impulses] = rd.readCoorImp(path, sort)

			if (speed) :
				impulses = impulseToSpeed(impulses)

			# Hold the sum of the impulses of all the particles around each node
			grid = [[[[0 for ax in range(size[3])] for z in range(size[2])] for y in range(size[1])] for x in range(size[0])]
			# Count number of particles associated to each node
			gridCount = [[[0 for z in range(size[2])] for y in range(size[1])] for x in range(size[0])]

			# Each particle is associated to it's closest node
			for i in range(len(coordinates[0])) :
				x = int(round(coordinates[0][i]/h))
				y = int(round(coordinates[1][i]/h))
				z = int(round(coordinates[2][i]/h))
				gridCount[x][y][z] += 1 #The node has one more particle
				for j in range(3) :
					grid[x][y][z][j] += impulses[j][i] #the 3 impulses are added

			# Looking for the right scale to apply depending on the sort of particles
			scales = [4, 5, 1]
			scale = scl*abs(scales[sort]/max(max(impulses[0]), max(impulses[1]), max(impulses[2])))

			# Meshgrid to be red by Mayavi
			nodesImpulses = np.meshgrid(np.empty([102]),
	                      np.empty([6]),
	                      np.empty([6]))

			for x in range(size[0]) :
				for y in range(size[1]) :
					for z in range(size[2]) :
						# Avoid 0 divisions
						if (gridCount[x][y][z] == 0) :
							gridCount[x][y][z] = 1

						for ax in range(size[3]) :
							# Each node receives the mean impulse of the particles associated
							nodesImpulses[ax][y][x][z] = (grid[x][y][z][ax]*scale)/gridCount[x][y][z]

			displayNodes3D(nodesImpulses, sort, scl)


def main() :
	parser = argparse.ArgumentParser(description="Displays 3D vectors of 1 particle out of 1000.")

	parser.add_argument("sort", type=int, choices=[1, 2, 3], help="Sorts of particles to display", nargs="+")
	parser.add_argument("-n", "--nodes", action="store_true", help="Dislpay mean impulses for node of the mesh")
	parser.add_argument("-S", "--Speed", action="store_true", help="Dislpay speeds instead of impulses")
	parser.add_argument("--scale", type=float, help="Size of the vectors", default=False)
	parser.add_argument("file", type=str, help="File to be displayed")

	args = parser.parse_args()

	#Parsing sorts
	sorts = [False, False, False]
	for sort in args.sort :
		if (sort == 1) :
			sorts[0] = True
		elif (sort == 2) :
			sorts[1] = True
		elif (sort == 3) :
			sorts[2] = True

	if (args.scale == False) :
		args.scale = 1

	if (args.nodes) :
		runNodes3D(args.file, sorts, args.scale, args.Speed)
	else :
		runParticles3D(args.file, sorts, args.scale, args.Speed)
	plt.show()

main()