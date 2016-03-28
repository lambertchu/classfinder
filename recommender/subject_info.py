from models import CompleteEnrollmentData, SubjectInfo

# Need: link to class description, link to class evaluations, prereqs/coreqs, 
# 		class ratings, when it's taken, what other classes taken with/before/after
def get_term_stats(subject):
	try:
		term_stats = SubjectInfo.objects.filter(subject=subject).values("term1", "term2", "term3", "term4", "term5", "term6", "term7", "term8")[0]
	except:
		term_stats = []

	term_list = []
	for term in sorted(term_stats):
		term_list.append((term, term_stats[term]))
	
	return term_list


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

	new_result = result.replace(" : null", " : None")		# format for conversion to Python dictionary
	dictionary = ast.literal_eval(new_result)				# conversion
	info = dictionary["item"]

	return info


# Offered in the spring/fall/both?