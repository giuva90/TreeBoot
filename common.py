"""
Common function and utilities
"""


def getDictKeyByValue(myDict: dict(), val) -> list:
	"""
	This function search the key of a given value in a dictionary
	:param myDict: the dictionary
	:param val: vale for search
	:return: the found key
	"""
	return myDict.keys()[list(myDict.values()).index(val)]
