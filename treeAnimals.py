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


# training_datafile = "InputData" + sep + "zoo_1.csv"
# questions_datafile = "InputData" + sep + "zoo_1_interaction.csv"


def init(dsname: str, csv_class_column_index: int, csv_columns_for_features: list):
	training_datafile = "InputData" + sep + dsname
	questions_datafile = training_datafile[:-4] + "_interaction.csv"
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

	data = dt.classify_by_asking_questions(root_node)
	data['questions'] = {}

	with open(questions_datafile, 'r') as csv_file:
		rows = reader(csv_file, delimiter=',')
		r = []
		for row in rows:
			r.append(row)
		numbers = r[0]
		del r[0]
		nQuestions = int(numbers[0])

		for i in range(nQuestions - 1):
			if r[i][0][0] == '#': continue
			data['questions'][r[i][0]] = r[i][1]
	data['dt'] = dt
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
