#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import sys

if sys.version_info[0] == 3:
	from DTC.DecisionTree import __version__
	from DTC.DecisionTree import __author__
	from DTC.DecisionTree import __date__
	from DTC.DecisionTree import __url__
	from DTC.DecisionTree import __copyright__

	from DTC.DecisionTree import DecisionTree
	from DTC.DecisionTree import EvalTrainingData
	from DTC.DecisionTree import DTIntrospection
	from DTC.DecisionTree import TrainingDataGeneratorNumeric
	from DTC.DecisionTree import TrainingDataGeneratorSymbolic

	from  DTC.DecisionTree import DTNode

else:
	# from DTC import __version__
	# from DTC import __author__
	# from DTC import __date__
	# from DTC import __url__
	# from DTC import __copyright__

	from DTC import DecisionTree
	from DTC import EvalTrainingData
	from DTC import DTIntrospection
	from DTC import TrainingDataGeneratorNumeric
	from DTC import TrainingDataGeneratorSymbolic

	from DTC import DTNode
