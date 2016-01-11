import sys
import time
import string
import csv
import ast
import psycopg2
from urllib2 import Request, urlopen

# connect to database
try:
    with open('pass.txt', 'r') as f:
    	for i, line in enumerate(f):
    		if i == 0:
    			password = line.rstrip('\n')
    		elif i == 1:
    			client_id = line.rstrip('\n')
    		elif i == 2:
    			client_secret = line.rstrip('\n')
    		elif i > 2:
    			break

	conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
except:
    print "Unable to connect to the database"
    sys.exit()
# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()


# Get list of all subjects
cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data")
subjects = [s[0] for s in cursor.fetchall()]
print len(subjects)

# List of any subjects that caused an error
errors = ["Errors:"]

print "Beginning extraction of descriptions..."
# add descriptions of all classes into database
with open("class_descriptions.csv", "wb") as f:
	writer = csv.writer(f)

	for subject in subjects[:10]:
		sub_clean = subject.strip()	# remove leading/trailing whitespace
		line = [sub_clean]

		# PROBLEM: some classes use description from a different class (i.e. 22.00)
		term = "2015FA"
		url = "https://mit-public.cloudhub.io/coursecatalog/v2/terms/%s/subjects/%s" % (term,sub_clean)

		try:
			q = Request(url)
			q.add_header('client_id', client_id)
			q.add_header('client_secret', client_secret)
			result = urlopen(q).read()
		except:
			print "Error: " + sub_clean
			errors.append(sub_clean)
			continue

		new_result = result.replace(" : null,", " : None,")		# sanitize result
		dictionary = ast.literal_eval(new_result)		# convert result to a Python dictionary
		info = dictionary["item"]

		# 'description', 'title', 'prerequisites', 'instructors', 'subjectId', 'cluster', 'academicYear', 'units': '4-0-8 HASS-S', 'optional': None, 'termCode': '2015FA'}
		line.append(info["title"])
		line.append(info["prerequisites"])
		line.append(info["units"])		# watch for auto-formatting into date
		line.append(info["optional"])
		line.append(info["instructors"])

		description = info["description"]
		line.append(description)

		token_list = description.translate(None, string.punctuation).split()	# tokenize
		stop_list = set('for a of the and to in with but how about such eg ie'.split())	# remove common words
		d_list = [x for x in token_list if x not in stop_list]
		line.append(d_list)


		# Insert time-relevance data
		cursor.execute("SELECT Term_Number FROM complete_enrollment_data WHERE Subject = %s", (subject,))
		terms = [t[0] for t in cursor.fetchall()]

		#for t in terms:


		writer.writerow(line)
	
	writer.writerow([])
	writer.writerow(errors)