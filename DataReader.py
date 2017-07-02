"""
This component allow the loading of the csv files.
All files are mapped in the dictionary data{} and the key is the name of the file
without the ".csv" at the end

The input is the list of the file that must be loaded.
The file are loaded from the folder "InputData"
"""
from dataset import Dataset
from csv import reader
from os import sep


def loadCsvFilesFromList(file_names=['LensData.csv'], parseID=True):
	"""
	This Function load the given list of file from ./InputData/
	ParseID is true by default
	:param file_names: a list of the csv file to be loaded from ./InputData/
	:param parseID: True as default, remove the first column if his name is id
	:return: a dictionary where the key is the name of the file without the ".csv" at the end and the data of the file
	"""
	data = {}
	for filename in file_names:
		current = filename[:-4]
		data[current] = loadCsv(filename, parseID)
	return data


def loadCsv(filename: str, parseID=True):
	"""
	:param filename: name of file to load
	:param parseID: True as default, remove the first column if his name is id
	:return: data matrix
	"""
	data = []
	with open("InputData" + sep + filename, 'r') as csv_file:
		rows = reader(csv_file, delimiter=';')
		for row in rows:
			data.append(row)
		if (data[0][0] == "id") & parseID:
			data = [row[1:] for row in data]
	return data


def parseDataset(data: list) -> Dataset:
	"""
	This function parse the dataset and transform all the textual field as numeric
	:param data: the data from csv to parse
	:return: 
	"""
	ds = Dataset()
	ds.data = [row[:-1] for row in data[1:]]
	# Computing the classes
	cls = [a[-1] for a in data[1:]]  # The classes are read from the last column of the loaded csv
	ct = 0
	for c in cls:
		if not ds.classesNames.has_key(c):
			ds.classesNames[c] = ct
			ct += 1
	for i in range(1, len(data) - 1):  # Make the class substitution
		ds.data[i][-1] = ds.classesNames[data[i][-1]]

	# Computing the data
	for c in range(0, len(data[0]) - 1):  # for all columns
		if any(isinstance(s, str) for s in data[:][c]):
			cls = [a[c] for a in data[1:]]
			ct = 0
			ds.ColumnConversionTable[c] = dict()
			for e in cls:
				if not ds.ColumnConversionTable[c].has_key(e):
					ds.ColumnConversionTable[c][e] = ct
					ct += 1
			for i in range(1, len(data) - 1):  # Make the class substitution
				ds.data[i][c] = ds.data[]
	return ds
