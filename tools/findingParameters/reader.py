from netCDF4 import Dataset
import numpy as np
import sys
import struct
import numpy.ma as ma
import os

#returns "<ldd...(size)...ddl"
def createFormatInt8(size):
	form = "<l"
	for h in range(0,size):
		form += "d"
	form += "l"
	return form

#Openning repertories from repPath
def openRep(files) :
	for i in range(len(files)) :
		if ((files[i][-3:] != "dat") and (files[i][-2:] != "nc")) : #if it's a repertory
			repoPath = files[i]

			#adding '/' if necessary
			if (files[i][-1] != "/") : 
				repoPath += "/"

			#storing all the paths of the repertory
			tmpFiles = []
			for filePath in os.listdir(files[i]) :
				if ((filePath[-3:] == "dat") or (filePath[-2:] == "nc")) :
					tmpFiles += [repoPath + filePath]

			#including all the files of the repertory
			files = files[:i] + tmpFiles + files[i+1:]
	
	return files


#DISPLAY IMPULSES

#Select the reader corresponding to the file format
def readImpulse(nameFile, sort, ax) :
	output = []
	if (nameFile[-3:] == "dat") :
		output = readImpulseDAT(nameFile, sort, ax)
	elif (nameFile[-2:] == "nc") :
		output = readImpulseCDF(nameFile, sort, ax)
	else :
		print("Wrong file format !")
	return output

#Reads 'ax' axis impulses from sort 'sort' in DAT format
def readImpulseDAT(file, sort, ax) :
	try:
		f = open(file, "rb") #read binary
		form = createFormatInt8(3672) # "<ld...dl"

		#Skipping fields
		for x in range(0,12):
			#r receive dat string (binary ?)
			f.read(29384)

		#Skipping sorts
		for i in range(sort) :
			r = f.read(32)
			infos = struct.unpack("<ldddl",r)

			size = int(infos[1])
			for x in range(0,6):
				f.read(size*8+8)

		#Reading sort's infos
		r = f.read(32)#32bytes (Number for Fortan, nb of particles in sort, charge sort, mass sort, Number for Fortran)

		infos = struct.unpack("<ldddl",r)

		size = int(infos[1])

		#Impulses
		impulses = []
		form = createFormatInt8(size)

		#Skippin axis
		for x in range(3+ax) :
			f.read(size*8+8)
		
		r = f.read(size*8+8)
		struc = struct.unpack(form, r)

		for i in range(0,size):
			impulses += [struc[i+1]]

	except IOError:
		print("Error")

	finally:
		f.close()
	
	return impulses

#Reads 'ax' axis impulses from sort 'sort' in netcdf format
def readImpulseCDF(file, sort, ax) :
	data = Dataset(file, "r", format="NETCDF4")

	axis = ["x", "y", "z"]
	num = ["0", "1", "2"]
	
	tmpImp = "Impulses_" + axis[ax] + num[sort]

	impulses = ma.getdata(data.variables[tmpImp][:])

	return impulses


def readCoorImp(path, sort) :
	output = []
	if (path[-3:] == "dat") :
		output = readCoorImpDAT(path, sort)
	elif (path[-2:] == "nc") :
		output = readCoorImpCDF(path, sort)
	else :
		print("Wrong file format !")
	return output


def readCoorImpDAT(path, sort) :
	try:
		f = open(file, "rb") #read binary
		form = createFormatInt8(3672) # "<ld...dl"

		#Skipping fields
		for x in range(0,12):
			#r receive dat string (binary ?)
			f.read(29384)

		#Skipping sorts
		for i in range(sort) :
			r = f.read(32)
			infos = struct.unpack("<ldddl",r)

			size = int(infos[1])
			for x in range(0,6):
				f.read(size*8+8)

		#Reading sort's infos
		r = f.read(32)#32bytes (Number for Fortan, nb of particles in sort, charge sort, mass sort, Number for Fortran)

		infos = struct.unpack("<ldddl",r)

		size = int(infos[1])

		#Coordinates/Impulses
		CoorImp = np.zeros((6,size),dtype = 'd')
		form = createFormatInt8(size)

		for x in range(0,6):
			r = f.read(size*8+8)
			structure = struct.unpack(form, r)
			for i in range(0,size):
				CoorImp[x][i] = structure[i+1]

	except IOError:
		print("Error")

	finally:
		f.close()
	
	return [CoorImp[:3], CoorImp[3:]]


def readCoorImpCDF(file, sort) :
	data = Dataset(file, "r", format="NETCDF4")

	axis = ["x", "y", "z"]
	num = ["0", "1", "2"]

	coordinates = [[] for i in range(3)]
	impulses = [[] for i in range(3)]

	for ax in range(3) :
			tmpCoor = "Coordinates_" + axis[ax] + num[sort]
			coordinates[ax] = ma.getdata(data.variables[tmpCoor][:])

			tmpImp = "Impulses_" + axis[ax] + num[sort]
			impulses[ax] = ma.getdata(data.variables[tmpImp][:])

	return [coordinates, impulses]


def readAllCoorImp(path) :
	output = []
	if (path[-3:] == "dat") :
		output = readAllCoorImpDAT(path)
	elif (path[-2:] == "nc") :
		output = readAllCoorImpCDF(path)
	else :
		print("Wrong file format !")
	return output


def readAllCoorImpDAT(file) :
	try:
		f = open(file, "rb") #read binary
		form = createFormatInt8(3672) # "<ld...dl"

		#Skipping fields
		for x in range(0,12):
			#r receive dat string (binary ?)
			f.read(29384)

		coorImp = []
		coordinates = []
		impulses = []

		for sort in range(3) :
			r = f.read(32)
			infos = struct.unpack("<ldddl",r)
			size = int(infos[1])

			#Coordinate/Impulses
			coorImp = coorImp + [np.zeros((6,size),dtype = 'd')]
			form = createFormatInt8(size)

			for x in range(0,6):
				r = f.read(size*8+8)
				struct1 = struct.unpack(form, r)
				for i in range(0,size):
					coorImp[sort][x][i] = struct1[i+1]

			coordinates = coordinates + [coorImp[sort][:3]]
			impulses = impulses + [coorImp[sort][3:]]


	except IOError:
		print("Error")

	finally:
		f.close()
	
	return [coordinates, impulses]


def readAllCoorImpCDF(file) :
	data = Dataset(file, "r", format="NETCDF4")

	axis = ["x", "y", "z"]
	num = ["0", "1", "2"]

	coordinates = [[[] for j in range(3)] for i in range(3)]
	impulses = [[[] for j in range(3)] for i in range(3)]

	for sort in range(3) :
		for ax in range(3) :
				tmpCoor = "Coordinates_" + axis[ax] + num[sort]
				coordinates[sort][ax] = ma.getdata(data.variables[tmpCoor][:])

				tmpImp = "Impulses_" + axis[ax] + num[sort]
				impulses[sort][ax] = ma.getdata(data.variables[tmpImp][:])

	return [coordinates, impulses]


#READ FIELDS

#Launch a reader depending on the file format
#sort = 0/1/2/3
def readField(nameFile, sort) :
	output = []
	if (nameFile[-3:] == "dat") :
		output = readFieldDAT(nameFile, sort)
	elif (nameFile[-2:] == "nc") :
		output = readFieldCDF(nameFile, sort)
	else :
		print("Wrong file format !")
	return output


#Returns x-values of one fields :
#[F[x], F[y], F[z]]
#F[X] = tab[102][6][6]
def readFieldCDF(nameFile, sort) :
	data = Dataset(nameFile, "r", format="NETCDF4")

	fieldsName = ["E", "M", "J", "Q"]
	x = "x"

	tmp = fieldsName[sort] + x 
	field = ma.getdata(data.variables[tmp])

	return field


#Returns x-values of one fields :
#[F[x], F[y], F[z]]
#F[X] = tab[102][6][6]
def readFieldDAT(nameFile, sort) :
	print("File : \"", nameFile, "\"")
	# print("Reading ...\n")

	try:
		f = open(nameFile, "rb") #read binary
		field = np.zeros((102,6,6),dtype='d')
		form = createFormatInt8(3672) # "<ld...dl"

		#skipping fields
		for x in range(sort) :
			f.read(29384)


		#r receive dat string (binary ?)
		r = f.read(29384)
		#v recoit python string
		v = struct.unpack(form, r)
		tmp = 1
		for i in range(0,102):
			for j in range(0,6):
				for k in range(0,6):
					field[i][j][k] = v[tmp]
					tmp+=1
	except IOError:
		print("Error")

	finally:
		f.close()
		# print("OK")
		#field = [E[3],M[3],C[3],E2[3]]

		return field


#READ ONLY ELECTRIC FIELD

#Launch a reader depending on the file format
def readElec(nameFile) :
	output = []
	if (nameFile[-3:] == "dat") :
		output = readElecDAT(nameFile)
	elif (nameFile[-2:] == "nc") :
		output = readElecCDF(nameFile)
	else :
		print("Wrong file format !")
	return output

#Returns All fields values :
#[E[x], E[y], E[z], M[x], M[y], M[z], C[x], C[y], C[z], E2[x], E2[y], E2[z]]
#E[X] = tab[102][6][6]
def readElecCDF(nameFile) :
	data = Dataset(nameFile, "r", format="NETCDF4")

	fields = []

	axis = ["x", "y", "z"]

	for i in range(3) :
		tmp = "E" + axis[i] 
		fields += [ma.getdata(data.variables[tmp])]

	return fields

#Returns all field values :
#[E[x], E[y], E[z], M[x], M[y], M[z], C[x], C[y], C[z], E2[x], E2[y], E2[z]]
#E[X] = tab[102][6][6]
def readElecDAT(nameFile) :
	print("File : \"", nameFile, "\"")
	# print("Reading ...\n")

	try:
		f = open(nameFile, "rb") #read binary
		fields = np.zeros((3,102,6,6),dtype='d')
		form = createFormatInt8(3672) # "<ld...dl"

		for x in range(0,3):
			#r receive dat string (binary ?)
			r = f.read(29384)
			#v recoit python string
			v = struct.unpack(form, r)
			tmp = 1
			for i in range(0,102):
				for j in range(0,6):
					for k in range(0,6):
						fields[x][i][j][k] = v[tmp]
						tmp+=1
	except IOError:
		print("Error")

	finally:
		f.close()
		# print("OK")
		#fields = [E[3],M[3],C[3],E2[3]]

		return fields