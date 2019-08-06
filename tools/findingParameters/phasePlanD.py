import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import reader as rd
import multiprocessing as mp
import argparse

import time


#Returns the velocity of a particle (following axis) from it's impulses
def velocity(px, py, pz) :
	return ( px*( 1/((px**2 + py**2 + pz**2)**0.5) ) )


def displayPhasePlanDiagram(index, speed, coordinates, deltaColor) :#col, nbBatchs) :
	#colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

	speeds = [speed[index[i]] for i in range(len(index))]
	coor = [coordinates[index[i]] for i in range(len(index))]

	plt.plot(coor, speeds, 'ro', markersize=0.2, label="", color=(deltaColor, 0.25, 0.25))#color=colors[col%len(colors)])


#Converting x-impulses into speeds
def speedFromImp(impulses) :
	speed = []
	for i in range(len(impulses[0])) :
		gamma = (impulses[0][i]**2 + impulses[1][i]**2 + impulses[2][i]**2 )**0.5
		speed += [impulses[0][i] / gamma]

	return speed

def tmp() :
	# Define an output queue
	output = mp.Queue()

	impulses = [impulses[0][:2150], impulses[1][:2150], impulses[2][:2150]]

	#Determining the repartition oftasks betweens processes
	nbCPU = mp.cpu_count()
	nbTasks = len(impulses[0])//nbCPU
	tasks = [0] + [nbTasks*i for i in range(1,nbCPU+1)]
	tasks[-1] = len(impulses[0])

	# Setup a list of processes that we want to run
	imp = []
	for i in range(nbCPU) :
		imp += [[impulses[0][tasks[i]:tasks[i+1]], impulses[1][tasks[i]:tasks[i+1]], impulses[2][tasks[i]:tasks[i+1]]]]
	
	processes = [mp.Process(target=speedPara, args=(imp[i], i, output)) for i in range(nbCPU)]

	# Run processes
	for p in processes:
	    p.start()

	# Exit the completed processes
	for p in processes:
	    p.join()

	print("done")
	# Get process results from the output queue
	speeds = sortSpeeds([output.get() for p in processes])
	print("block")

	return speeds


def speedPara(impulses, index, output) :
	speed = []
	for i in range(len(impulses[0])) :
		gamma = (impulses[0][i]**2 + impulses[1][i]**2 + impulses[2][i]**2 )**0.5
		speed += [abs(impulses[0][i]) / gamma] #ABS !!!??

	output.put([index,speed])


def filterCoorImp(coordinates, impulses, step) :
	liteCoor = [[[] for ax in range(3)] for sort in range(3)]
	liteImp = [[[] for ax in range(3)] for sort in range(3)]

	for sort in range(3) :
		for ax in range(3) :
			liteCoor[sort][ax] = [coordinates[sort][ax][i] for i in range(0, len(coordinates[sort][ax]), step)]
			liteImp[sort][ax] = [impulses[sort][ax][i] for i in range(0, len(impulses[sort][ax]), step)]

	return [liteCoor, liteImp]

#Returns the processes results in the right order
def sortSpeeds(speeds) :
	result = []
	
	tmp= 0
	while (tmp<len(speeds)) :
		for i in range(len(speeds)) :
			if (speeds[i][0] == tmp) :
				result += speeds[i][1]
				tmp += 1

	return result


def makeCmap(nbBatchs) :
	# rgbs = []
	# nbCol = nbBatchs//5
	# for i in range(nbCol) :
	# 	rgbs += [(1, min(i/nbCol, 1), 0)]
	
	# for i in range(nbCol-1, -1, -1) :
	# 	rgbs += [(max(i/nbCol,0), 1, 0)]
	
	# for i in range(nbCol) :
	# 	rgbs += [(0, 1, min(i/nbCol, 1))]
	
	# for i in range(nbCol-1, -1, -1) :
	# 	rgbs += [(1, max(i/nbCol, 1), 1)]


	# cmap = matplotlib.colors.ListedColormap(rgbs)
	cmap =  matplotlib.colors.ListedColormap([(i/nbBatchs,0.25,0.25) for i in range(nbBatchs)])

	cmap.set_over('-1')
	cmap.set_under('1')

	return cmap


#returns the index of particles classified by speed
def init(file, step, nbBatchs) :
	#Load first file
	[coordinates, impulses] = rd.readAllCoorImp(file)
	[coordinates, impulses] = filterCoorImp(coordinates, impulses, step)

	#batchs for 3 sorts of particles
	indexs = []
	speeds = []

	maxSpeed = 0
	minSpeed = 0
	delta = 0

	for sort in range(3) :
		#each batch correspond to the particles with speed between v and v+dv
		batchs = [[] for i in range(nbBatchs)]

		imp = impulses[sort]
		#Converting x-imp into speeds
		begSpeed = time.time()
		speed = speedFromImp(imp)
		endSpeed = time.time()
		print("Converting speed :", endSpeed-begSpeed)

		maxSpeed = max(speed)*1.0001
		minSpeed = min(speed)*0.9999
		delta = (maxSpeed-minSpeed)/nbBatchs

		for i in range(len(speed)) :
			vi = int((speed[i]-minSpeed)/delta)
			batchs[vi] += [i]

		indexs += [batchs]
		speeds += [speed]

	output = [indexs, speeds]

	#Defining a new figure
	fig = plt.figure(file, figsize=(20.0, 5.0))
	for sort in range(3) :
		#Each sort of particles has it's own subfigure
		sp = fig.add_subplot(1, 3, sort+1)
		sp.title.set_text("Sort " + str(sort+1))
		plt.xlabel('x')
		plt.ylabel('Velocity x')

		#Displaying each batch of particle with a different color
		for batch in range(nbBatchs) :
			displayPhasePlanDiagram(indexs[sort][batch], speeds[sort], coordinates[sort][0], batch/nbBatchs)

	#Colorbar
	ax1 = fig.add_axes([0.92, 0.125, 0.03, 0.75])
	cmap = makeCmap(nbBatchs)
	norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
	cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='vertical')

	return output


#Represents the velocity of particles depending on the time
#All particles are classified in "batchs" from the initialization depending on their velocity
def runPhasePlan(files, nbBatchs, step) :
		#INITIALISATION

	#Setting default figure size
	# matplotlib.rcParams['figure.figsize'] = (20.0, 5.0)

	#Classify particles by their index, depending on their speed, display the result and return classification
	[indexs, speeds] = init(files[0], step, nbBatchs)

		#DISPLAYING ALL FILES

	for file in range(1, len(files)) :
		[coordinates, impulses] = rd.readAllCoorImp(files[file])
		[coordinates, impulses] = filterCoorImp(coordinates, impulses, step)

		#Defining a new figure for each file
		fig = plt.figure(files[file], figsize=(20.0, 5.0))
		for sort in range(3) :
			#Each sort of particles has it's own subfigure
			sp = fig.add_subplot(1, 3, sort+1)
			sp.title.set_text("Sort " + str(sort+1))
			plt.xlabel('x')
			plt.ylabel('Velocity x')

			#Getting the speed
			speeds = speedFromImp(impulses[sort])

			#Displaying each batch of particles with a different color
			for batch in range(nbBatchs) :
				displayPhasePlanDiagram(indexs[sort][batch], speeds, coordinates[sort][0], batch/nbBatchs)

		#Colorbar
		ax1 = fig.add_axes([0.92, 0.125, 0.03, 0.75])
		cmap = makeCmap(nbBatchs)
		norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
		cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='vertical')

	plt.show()


def main() :
	parser = argparse.ArgumentParser(description="Classify particles in batch depending on there impulse x and display their evolution file to file")

	parser.add_argument("-n", "--number", type=int, help="Number of batch to make out of impulses/speed")
	parser.add_argument("-f", "--frequence", type=int, help="Display only one particle out of \'frequence\'")
	parser.add_argument("FILE", type=str, help="List of files to be displayed", nargs="+")

	args = parser.parse_args()

	files = rd.openRep(args.FILE)

	if (args.number == None) :
		args.number = 100
	if (args.frequence == None) :
		args.frequence = 1

	runPhasePlan(files, args.number, args.frequence)

main()