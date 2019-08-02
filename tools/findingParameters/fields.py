import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import reader as rd
import argparse


def findSinFunction(field) :
	#DETERMINIG AMPLITUDE
	amplitude = max(np.abs(field))


	#DETERMINIG ANGULAR FREQUENCY
	# computing fourier transform
	fourier = np.fft.fft(field)

	# computing frequencies fourier transform
	freq = np.fft.fftfreq(len(field))

	#Getting real part of Fourrier transformed field
	realFourrier = np.real(fourier)

	#Searching for the fundamental frequency
	tmpAF = max(realFourrier)
	frequence = 0
	for i in range(len(realFourrier)) :
		if (realFourrier[i] > 0.9*tmpAF) :
			if (freq[i] > 0) :
				frequence = freq[i]

	angularFrequence = frequence*2*np.pi


	#DETERMINING PHASE
	phase = 0

	return (amplitude, angularFrequence, phase)


def sinusoidal(x, amplitude, angularFreq, phase) :
	return amplitude*np.sin(angularFreq*x + phase)


#Displays the value of the Electric field following x axis
def displayField(field, y, z, curve) : #field[102][6][6]
	abscissa = np.arange(0, len(field), 1)
	axis = [] + [field[i][y][z] for i in range(len(field))] #Convert matrix[x][y][z] to list[102]

	plt.plot(abscissa, axis, markersize=0.2, color='red', label="data")
	plt.legend()

	# red_patch = mpatches.Patch(color='red', label='data')
	# plt.legend(handles=[red_patch])

	if (curve) :
		#Finding the parameters of the sine function that describes the field
		(amplitude, angularFreq, phase) = findSinFunction(axis)

		print("Amplitude", amplitude, "- Angular Frequence", angularFreq, "- Phase", phase)

		#Applying the function to compare with the data
		fSin = sinusoidal(abscissa, amplitude, angularFreq, phase)

		plt.plot(abscissa, fSin, markersize=0.1, color='green', label="curve")
		plt.legend()

		# green_patch = mpatches.Patch(color='green', label='curve')
		# plt.legend(handles=[green_patch])


#Initializes arguments and launch display_impulses function
def runField(files, curve, sorts=[0], y=3, z=2) :
	#sort = [0/1/2/3] <=> Electric, Magnetic, Currant or HalfStep Electric
	fields = ["Electric", "Magnetic", "Currant", "HalfStep Magnetic"]

	for file in files :

		#load data
		figures = []
		for sort in sorts :
			field = rd.readField(file, sort) #field[102][6][6]
			figures += [plt.figure(file + " - " + fields[sort] + " field")]
			plt.xlabel('Position')
			yLab = fields[sort] + " Field x"
			plt.ylabel(yLab)
			plt.title("Y = " + str(y) + " - Z = " + str(z))
			displayField(field, y, z, curve)

	plt.show()


def main() :
	parser = argparse.ArgumentParser(description="Displays the value of a field following x axis.")

	parser.add_argument("sort", type=int, choices=[0, 1, 2, 3], help="Sorts of field", nargs="+")
	# \n0 : Electric\n1 : Magnetic\n2 : Currant\nHalf-Step Electric
	parser.add_argument("yz", type=int, help="Line of the mesh to be displayed between 0 & 5", nargs=2)
	parser.add_argument("-c", "--curve", help="Display the curve followed by the field", action="store_true")
	parser.add_argument("FILE", type=str, help="List of files to be displayed", nargs="+")

	args = parser.parse_args()

	#Parsing sorts
	sorts = args.sort

	files = rd.openRep(args.FILE)

	[y, z] = args.yz

	#Launching the field display
	runField(files, args.curve, sorts, y, z)

main()