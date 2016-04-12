from models import CompleteEnrollmentData, SubjectInfo

# Need: link to class description, link to class evaluations, prereqs/coreqs, 
# 		class ratings, when it's taken, what other classes taken with/before/after
def get_term_stats(subject):
	# Get term-relevance data
	subject = subject.upper()
	terms = CompleteEnrollmentData.objects.filter(subject=subject).values_list("term_number", flat=True)

	# Map term_number to its frequency
	term_dict = {}
	for t in terms:
		if t in term_dict:
			term_dict[t] += 1
		else:
			term_dict[t] = 1

	return term_dict


def get_online_info(subject):
	import ast
	from urllib2 import Request, urlopen

	client_id = "ea65df8068bd4a0f8ed9ebda0d2067b5"
	client_secret = "7e37b0d1c7a547858D667BC330A32134"

	TERM = "2016SP"
	URL = "https://mit-public.cloudhub.io/coursecatalog/v2/terms/%s/subjects/%s" % (TERM, subject)

	try:
		q = Request(URL)
		q.add_header('client_id', client_id)
		q.add_header('client_secret', client_secret)
		result = urlopen(q).read()
	except:
		print "Error: %s" % subject
		return None

	new_result = result.replace(" : null", " : None")		# format for conversion to Python dictionary
	dictionary = ast.literal_eval(new_result)				# conversion
	info = dictionary["item"]

	return info


# Offered in the spring/fall/both?