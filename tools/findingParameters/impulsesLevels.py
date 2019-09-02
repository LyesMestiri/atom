import argparse

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import statistics
import numpy.ma as ma
import os
import multiprocessing as mp
import reader as rd

# Normal Law
def norm(x, amplitude, mean, variance) :
	return (amplitude*np.exp(-(x-mean)**2/(2*variance)))


# Returns an array classifying particles by growing categories of impulse
# categories[n] counts the number of particles with an impulse in [minim+n*delta, minim+(n+1)*delta]
def categorize(impulses, size, minim, delta) :
	categories = [0 for i in range(size)]

	for x in impulses : 
		categories[int((x - minim)/delta)] += 1

	return categories


# Send the mean to the output
def partMean(impulses, output) :
	m = statistics.mean(impulses) # compute mean
	output.put(m)


# Send the variance to the output
def partVariance(impulses, output) :
	var = statistics.variance(impulses) # compute variance
	output.put(var)


# Return the combination of all the variances
def groupVar(variances, tasks) :
	var = 0

	for i in range(len(variances)) :
		var += variances[i]*(tasks[i+1]-tasks[i])

	return (var/(tasks[-1]))


# Displays the number of particles in each impulses-category of width delta
def displayImpulse(impulses, velocity, categories, delta, sort, coordinate, options, col, file) :
	#Load options & variables
	[sep, showMean, showVariance, showCurve] = options
	colors = ['b', 'r', 'k', "g", 'c', 'm', 'y']
	axis = ['x', 'y', 'z']

	#Title & Axis of the graph
	title = "Sort " + str(sort+1) + " - Axis " + str(axis[coordinate])
	plt.title(title)
	ylabel = "Number particles"
	plt.ylabel(ylabel)
	xlabel = str(axis[coordinate])
	plt.xlabel(xlabel)


	if (showMean) :
		# determine yAxis max which corresponds to the impulse level containing the more particles
		amplitude = max(categories) - min(categories)

		# Define an output queue for parallel computation
		output = mp.Queue()

		# Determining the repartition of tasks betweens processes
		nbCPU = mp.cpu_count()
		nbTasks = len(impulses)//nbCPU
		tasks = [0] + [nbTasks*i for i in range(1,nbCPU+1)]
		tasks[-1] = len(impulses)

		# Setup a list of processes that we want to run
		processes = [mp.Process(target=partMean, args=(impulses[tasks[i]: tasks[i+1]], output)) for i in range(nbCPU)]

		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
		    p.join()

		# Get process results from the output queue
		mean = statistics.mean([output.get() for p in processes])
		print("Mean for Sort " + str(sort+1) + " - " + axis[coordinate] + " axis : " + str(mean)) # print mean

		# Displays Mean
		plt.axvline(x = mean, markersize=0.1, color=colors[col%len(colors)])
		plt.text(x = mean, y=0.75*amplitude, s="m:"+str(mean), verticalalignment='center', color=colors[col%len(colors)])


	if (showVariance) :
		# Define an output queue
		output = mp.Queue()

		# Determining the repartition oftasks betweens processes
		nbCPU = mp.cpu_count()
		nbTasks = len(impulses)//nbCPU
		tasks = [0] + [nbTasks*i for i in range(1,nbCPU+1)]
		tasks[-1] = len(impulses)

		# Setup a list of processes that we want to run
		processes = [mp.Process(target=partVariance, args=(impulses[tasks[i]: tasks[i+1]], output)) for i in range(nbCPU)]

		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
		    p.join()

		# Get process results from the output queue
		variance = groupVar([output.get() for p in processes], tasks)
		
		print("Variance for Sort " + str(sort+1) + " - " + axis[coordinate-1] + " axis : " + str(variance)) # print variance 
		
		# Displays Variance
		plt.text(x = mean, y=0.7*amplitude, s="v:"+str(variance), verticalalignment='center', color=colors[col%len(colors)])


	if (showCurve) :
		# Display the function followed by the impulses
		fImpulses = norm(velocity, amplitude, mean, variance)
		label = "sort " + str(sort+1) + " - axis " + str(coordinate+1) 
		plt.plot(velocity, fImpulses, markersize=0.1, label=label, color=colors[col%len(colors)])


	# Display the Impulses classified by categories
	plt.plot(velocity, categories, 'ro', markersize=0.2, label=file, color=colors[col%len(colors)])
	plt.legend(loc="upper right", markerscale=10)
	

# Calculates all that is needed to display the impulses
def prepareDisplay(files, sort, ax, options, nbLvl) :
	axis = ['x', 'y', 'z']
	sep = options[0]
	for i in range(len(files)) :
		# load data
		impulses = rd.readImpulse(files[i], sort, ax)


		# Getting bounds of Impulses
		minim = min(impulses)
		maxim = max(impulses)

		# Difference between 2 impulse levels
		delta = (maxim*1.0001-minim)/nbLvl

		# Array representing the categories of impulses (X axis)
		velocity = np.arange(minim, maxim, delta)

		# Array containing the number of particles in each categories (Y axis)
		categories = categorize(impulses, nbLvl, minim, delta)


		if sep :
			name = files[i] + " : sort " + str(sort+1) + " - axis " + axis[ax] 
		else :
			name = "Sort " + str(sort+1) + " - Axis " + axis[ax]
		fig = plt.figure(name)
		fig.suptitle("Delta = " + str(delta))

		displayImpulse(impulses, velocity, categories, delta, sort, ax, options, i, files[i])


# displays the impulses in the right order
# depending on the sort, the axis and the file
def orderTasks(filesPaths, sorts, axis, options, nbLvl) :
	axisName = ["x", "y", "z"]

	for sort in range(len(sorts)) :
		if (sorts[sort]) :

			for ax in range(len(axis)) :
				if (axis[ax]) :
					prepareDisplay(filesPaths, sort, ax, options, nbLvl)
	plt.show()


def main() :
	parser = argparse.ArgumentParser(description="Display the number of particles classified by level of impulses.")

	parser.add_argument("-s", "--sort", type=int, choices=[1, 2, 3], help="Sorts of particles to display", nargs="+", required=True)
	parser.add_argument("-a", "--axis", type=str, choices=['x','y','z'], help="Axis to display", nargs="+", required=True)
	parser.add_argument("--sep", "--separated", action="store_true", help="Represent each file on different figures")
	parser.add_argument("-m", "--mean", action="store_true", help="Dislpay the mean impulse")
	parser.add_argument("-v", "--variance", action="store_true", help="Dislpay the variance of impulses")
	parser.add_argument("-c", "--curve", action="store_true", help="Dislpay the repartition curve of the particles")
	parser.add_argument("-n", "--numberLevels", type=int, help="Number of \'impulse levels\'")
	# parser.add_argument("-d", "--delta", type=float, help="Difference of impulse between 2 \'levels\'")
	parser.add_argument("-f", "--file", type=str, help="List of files to be displayed", nargs="+", required=True)

	args = parser.parse_args()

	# Parsing sorts
	sorts = [False, False, False]
	for sort in args.sort :
		if (sort == 1) :
			sorts[0] = True
		elif (sort == 2) :
			sorts[1] = True
		elif (sort == 3) :
			sorts[2] = True

	# Parsing axis
	axis = [False, False, False]
	for a in args.axis :
		if (a == "x") :
			axis[0] = True
		elif (a == "y") :
			axis[1] = True
		elif (a == "z") :
			axis[2] = True

	# Parsing other options
	options = [args.sep, args.mean, args.variance, args.curve]
	if (args.curve) :
		options[1] = True
		options[2] = True
	elif (args.variance) :
		options[1] = True

	if (args.numberLevels == None) :
		args.numberLevels = 1000

	# Parsing files
	files = rd.openRep(args.file)

	# Launching the impulse display
	orderTasks(files, sorts, axis, options, args.numberLevels)

main()