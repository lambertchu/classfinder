import sys
import csv
import psycopg2
from scipy import spatial

try:
    with open('pass.txt', 'r') as f:
        password = f.readline()
    conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
    print "Connected to database"
except:
    print "Unable to connect to the database"
    sys.exit()


# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()

# execute our query - get list of all classes
cursor.execute("SELECT DISTINCT Subject FROM enrollment_data")

# retrieve the records from the query
records = cursor.fetchall()     # list of tuples
print len(records)

# extract classes from records
classes = []
for record in records:
    classes.append(record[0])
num_classes = len(classes)

# create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}

# create nxn matrix with n = total number of classes
matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

# create nxn similarity table
similarity_table = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

# implementation of item-to-item CF
for cls in classes:
    print cls
    cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data WHERE Subject = %s", (cls,))
    records = cursor.fetchall()
    students = [student[0] for student in records]
    break
    for student in students:
        #print student
        cursor.execute("SELECT DISTINCT Subject FROM enrollment_data WHERE Identifier = %s", (student,))
        records = cursor.fetchall()
        subjects = [subject[0] for subject in records]
        #print len(subjects)
        
        for subject in subjects:    # subjects are the classes that student has taken
            matrix[class_table[cls]][class_table[subject]] += 1     # goes down column, then across the row

    for c in classes:
        # compute similarity between cls and c
        cls_list = matrix[class_table[cls]]
        c_list = matrix[class_table[c]]
        similarity = 1 - spatial.distance.cosine(cls_list, c_list)
        similarity_table[class_table[cls]][class_table[c]] = similarity


# use str.strip() method to remove whitespaces in class names
# output data to CSV
#with open("output.csv", "wb") as f:
#    writer = csv.writer(f)
#    writer.writerow(classes)
#    writer.writerows(similarity_table)
sys.exit()