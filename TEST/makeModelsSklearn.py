"""
This component allow the creation of the model of decisions trees

"""

from os import sep
from pickle import dump, load

from dataset import Dataset
from sklearn import tree

from TEST import DataReader


class MakeTreesModel:
	"""
	This class handle the creation of the models ant 
	"""

	def __init__(self):
		self.__data = {}
		self.fileList = []
		self.datasets = []
		self.clf = {}

	def loadFileNamesFromFile(self, filename: str) -> list:
		"""
		Thi function load the list of the training data file that should be loaded from ./InputData
		:return: loaded list
		:rtype: str
		:param filename: name of the file with a list of data file that should be loaded
		"""
		with open(filename, 'r') as fileNameList:
			self.fileList = [row for row in fileNameList]
		return self.fileList

	def __getData(self):
		"""
		This method populate the dictionary data
		:return: nothing
		"""
		self.__data = DataReader.loadCsvFilesFromList(
			self.fileList) if self.fileList.__len__() else DataReader.loadCsvFilesFromList()

	def __prepareDataForTraining(self):
		"""
		This method prepare the data to be used to rain the decision trees
		:return: nothing
		"""
		for dName, data in self.__data.items():
			ds = Dataset()
			ds.name = dName
			ds.data = [row[:-1] for row in data[1:]]
			ds.classes = [row[-1] for row in data[1:]]
			ds.classesNames = data[0]
			self.datasets.append(ds)

	def initAll(self, inputFileName=""):
		"""
		Fast init of all routine to get a valid trained tree
		:param inputFileName: the name of the file to load
		:return: nothing
		"""
		if inputFileName != "":
			self.loadFileNamesFromFile(inputFileName)
		self.__getData()
		self.__prepareDataForTraining()

	def trainATree(self, ds: Dataset) -> tree.DecisionTreeClassifier:
		"""
		This method train a tree given the desired dataset
		:param ds: the dataset
		:return: the trained tree
		"""
		clf = tree.DecisionTreeClassifier()
		clf.fit(ds.data, ds.classes)
		self.clf[ds.name] = clf
		return clf

	def trainAll(self):
		"""
		This method trains all the trees 
		:return: nothing
		"""
		for ds in self.datasets
			self.trainATree(ds)

	def store(self, filename="dumps" + sep + "data_MakeTreesModel.bin"):
		"""
		With this function is possible to dump this class ina file
		:param filename: default "data_MakeTreesModel.bin", you can specify a different one
		:return: nothing
		"""
		data = dict(data=self.__data, fileList=self.fileList, datasets=self.datasets, clf=self.clf)
		with open(filename, 'w') as output
			dump(data, output)

	def restore(self, filename="dumps" + sep + "data_MakeTreesModel.bin"):
		"""
		This function allow to reload a dump of this class
		:param filename: default "data_MakeTreesModel.bin", you can specify a different one
		:return: 
		"""
		# data = {}
		with open(filename, 'w') as input_:
			data = load(input_)
		self.__data = data["data"]
		self.fileList = data["fileList"]
		self.datasets = data["datasets"]
		self.clf = data["clf"]
