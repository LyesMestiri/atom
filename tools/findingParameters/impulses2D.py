import numpy as np
import matplotlib.pyplot as plt
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


#Generates a gnuplot file to be displayed using the commands :
#gnuplot
#scale = ?     --  (5000000/100/10) with respect to the sort of particle
#plot 'filePath' u 1:2:($3*scale):($4*scale) with vectors
def gnuplotFile(coordinates, impulses, sort, coordinate, dataPath) :
	axis = ['x', 'y', 'z']

	#Creating new file
	name = str(sort) + "_" + str(axis[coordinate[0]]) + "-" + str(axis[coordinate[1]]) + "_" + dataPath[-13:-3] + ".txt"
	file = open(name, "w")

	#variables to copy in the file
	x = ""
	y = ""
	vx = ""
	vy = ""

	# Gap between 2 nodes of the grid
	h = 1.255/100

	# Sum of impulses squarred among the particles 
	px = 0
	py = 0
	#pz = 0

	# Displaying 1 particle out of 1000 to be able to display vectors
	for i in range(0,len(coordinates[0]), 1000) :
		# Summing squarred impulses
		px += impulses[0][i]**2
		py += impulses[1][i]**2
		#pz += impulses[2][i]**2

		# Gettings values to write
		x = str(coordinates[0][i]/h)
		y = str(coordinates[1][i]/h)
		vx = str(impulses[0][i])
		vy = str(impulses[1][i])

		# Writting values in the file
		line = x + " " + y + " " + vx + " " + vy + "\n"
		file.write(line)
	
	file.close()

	print("Sort", sort, ":")
	print("px :", px)
	print("py :", py)
	#print("pz :", pz, "\n")


def run2D(dataPath, ax, speed) :
	sorts = [True, True, True]

	for sort in range(len(sorts)) :

		#Loading x-axis values
		coordinate = [0] #Values of the coordinates of the particles
		[coordinates, impulses] = rd.readCoorImp(dataPath, sort)

		if (speed) :
			impulses = impulseToSpeed(impulses)

		#Loading y-axis values
		if (ax == "y") :
			coordinate += [1]
			tmpCoorImp = rd.readCoorImp(dataPath, 1)
			coordinates += [tmpCoorImp[0]]
			impulses += [tmpCoorImp[1]]

		elif (ax == "z") :
			coordinate += [2]
			tmpCoorImp = rd.readCoorImp(dataPath, 2)
			coordinates += [tmpCoorImp[0]]
			impulses += [tmpCoorImp[1]]

		gnuplotFile(coordinates, impulses, sort, coordinate, dataPath)


def main() :
	parser = argparse.ArgumentParser(description="Generates a gnuplot files for 2D displaying for each 3 sorts of particles")

	parser.add_argument("axis", type=str, choices=["y","z"], help="Axis to display")
	parser.add_argument("-s", "--speed", action="store_true", help="Dislpay speeds instead of impulses")
	parser.add_argument("file", type=str, help="List of files to be displayed", nargs="+")

	args = parser.parse_args()

	files = rd.openRep(args.file)

	for file in files :
		run2D(file, args.axis, args.speed)

main()