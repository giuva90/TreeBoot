#!/usr/bin/env python
## classify_by_asking_questions.py

import DTC.DecisionTree as DecisionTree
from os import sep
from csv import reader


def convert(value):
	try:
		answer = float(value)
		return answer
	except:
		return value


def init(dsname: str, csv_class_column_index: int, csv_columns_for_features: list):
	"""
	This method init the tree structur, ready for interactive navigation.
	
	:param dsname: name of dataset file to be load. It must be under ./InpoutData/
	:param csv_class_column_index: index of (from 0) for the column that contain the class inside the dataset
	:param csv_columns_for_features: List of indexes of the column that contains the feature that should be considered
	:type csv_class_column_index: int
	:type csv_columns_for_features: List<int>
	"""
	training_datafile = "InputData" + sep + dsname
	interaction_datafile = training_datafile[:-4] + "_interaction.csv"
	dt = DecisionTree(training_datafile=training_datafile,
	                  csv_class_column_index=csv_class_column_index,
	                  csv_columns_for_features=csv_columns_for_features,
	                  entropy_threshold=0.00001,
	                  max_depth_desired=25,
	                  # debug1 = 1,
	                  # debug2 = 1,
	                  # debug3 = 1,
	                  )
	dt.get_training_data()
	dt.calculate_first_order_probabilities()
	dt.calculate_class_priors()

	root_node = dt.construct_decision_tree_classifier()

	# start importing the data about questions and features humanization
	data = dt.classify_by_asking_questions(root_node)
	data['dt'] = dt
	data['questions'] = {}
	data['featuresHumanization'] = {}
	data['classHumanization'] = {}
	data['interaction'] = {}

	with open(interaction_datafile, 'r') as csv_file:
		# rows = reader(csv_file, delimiter=',')
		r = [row.strip().split(',') for row in csv_file]
		numbers = r[0]
		del r[0]
		nQuestions = int(numbers[0])
		nFeatures = int(numbers[1])
		nClasses = int(numbers[2])

		for i in range(len(r)):
			if r[i][0][0] == "#":
				continue
			elif i <= nQuestions + 1:
				data['questions'][r[i][0]] = r[i][1]
			elif i <= nQuestions + nFeatures + 2:
				data['featuresHumanization'][r[i][0]] = r[i][1:]
			elif i <= nQuestions + nFeatures + nClasses + 3:
				data['classHumanization'][r[i][0]] = ",".join(r[i][1:])
			elif r[i][0] == 'singleAnswer':
				data['interaction']['singleAnswer'] = ",".join(r[i][1:])

			# # read data for questions
			# for i in range(nQuestions - 1):
			# 	if r[i][0][0] == "#":
			# 		continue
			# 	data['questions'][r[i][0]] = r[i][1]
			# 	r.pop(i)
			#
			# # read data for feature humanization
			# for i in range(nFeatures - 1):
			# 	if r[i][0][0] == "#":
			# 		continue
			# 	data['featuresHumanization'][r[i][0]] = r[i][1:]
			# 	r.pop(i)
			#
			# # read data for class answering
			# for i in range(nClasses - 1):
			# 	if r[i][0][0] == "#":
			# 		continue
			# 	data['classHumanization'][r[i][0]] = r[i][1:]
			# 	r.pop(i)

	return data


def interactByCommandLine(data):
	while not data['__stop']:
		toAsk = data['toAsk']
		if data['step'] == 1:
			if 'valueRange' in toAsk:
				# Se la featuere ha valore numerico compreso in un intervallo:
				user_value_for_feature = input(
					"\nWhat is the value for the feature '" + toAsk['feature'] + "'?" + "\n" +
					"Enter a value in the range: " + str(toAsk['valueRange']) + " => ")
				user_value_for_feature = convert(user_value_for_feature.strip())
				if toAsk['valueRange'][0] <= user_value_for_feature <= toAsk['valueRange'][1]:
					data['step'] = 0
					data['s'][toAsk['feature']] = user_value_for_feature
					data = dt.classify_by_asking_questions(data['actualNode'], data)
				else:
					print("Value not valid!")
					continue
			elif 'possibleAnswer' in toAsk.keys():
				# se la feature ha valore simbolico
				user_value_for_feature = input("\nWhat is the value for the feature '" + toAsk['feature'] +
				                               "'?" + "\n" + "Enter one of: " + str(toAsk['possibleAnswer']) + " => ")
				user_value_for_feature = convert(user_value_for_feature.strip())
				if user_value_for_feature in toAsk['possibleAnswer']:
					data['step'] = 0
					data['toAsk']['givenAnswer'] = user_value_for_feature
					data = dt.classify_by_asking_questions(data['actualNode'], data)
				else:
					print("Value not valid!")
					continue
		else:
			print('che cio fccio qui????')


def processOutputForCommandLine(data):
	classification = data['a']
	solution_path = classification['solution_path']
	del classification['solution_path']
	which_classes = list(classification.keys())
	which_classes = sorted(which_classes, key=lambda x: classification[x], reverse=True)
	print("\nClassification:\n")
	print("     " + str.ljust("class name", 30) + "probability")
	print("     ----------                    -----------")
	for which_class in which_classes:
		if which_class is not 'solution_path':
			print("     " + str.ljust(which_class, 30) + str(classification[which_class]))

	print("\nSolution path in the decision tree: " + str(solution_path))
	print("\nNumber of nodes created: " + str(root_node.how_many_nodes()))
