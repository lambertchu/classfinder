import json
from sets import Set


"""
Read requirements for the given major from the json file
"""
def read_file(major):
	with open('recommender/static/recommender/degree_requirements.json', 'r') as f:
		data = json.load(f)
	return data[major]


"""
Helper method to process lists in the json file
"""
def process_list(item, classes_taken):
	candidate_classes = Set([])
	num_required = item[0]
	count = 0
	for i in xrange(1, len(item)):
		if item[i] in classes_taken:
			count += 1
	if count < num_required:
		for i in xrange(1, len(item)):
			if item[i] not in classes_taken:
				candidate_classes.add(item[i])
	return candidate_classes


"""
Returns a list of candidate classes the student should take
"""
def get_classes_to_take(major, classes_taken, reqs=None):
	if reqs == None:
		reqs = read_file(major)
	all_classes = Set([])
	to_take = Set([])

	for item in reqs:
		if type(item) == str or type(item) == unicode:
			if item not in classes_taken:
				to_take.add(item)

		elif type(item) == list:
			is_nested = False
			for i in item:
				if type(i) == list:
					is_nested = True

			if is_nested:	# nested list
				possible_classes = Set([])
				num_required = item[0]
				count = 0
				for i in item:
					if type(i) == str or type(i) == unicode:
						if i not in classes_taken:
							possible_classes.add(i)
						else:
							count += 1

					elif type(i) == list:
						ret_classes = process_list(i, classes_taken)
						if len(ret_classes) > 0:
							possible_classes = possible_classes.union(ret_classes)
						else:
							count += 1

				if count < num_required:
					to_take = to_take.union(possible_classes)

			else:			# regular list
				candidate_classes = process_list(item, classes_taken)
				to_take = to_take.union(candidate_classes)
				
	return list(to_take)