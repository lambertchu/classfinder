import sys
import csv
import psycopg2


""" Connect to database """
try:
    with open('pass.txt', 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                password = line.rstrip('\n')
            else:
                break
                
    conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
except:
    print "Unable to connect to the database"
    sys.exit()
# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()


""" Get list of all classes """
cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data")
classes = [cl[0] for cl in cursor.fetchall()]
num_classes = len(classes)
print num_classes

""" Create hash table with keys = classes and values = index in list """
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}


""" Get distinct majors """
cursor.execute("SELECT DISTINCT Major1 FROM complete_enrollment_data;")
majors = [m[0] for m in cursor.fetchall()]
print len(majors)


""" Create nxn matrices (to be stored in database) """
for major in majors:
    print "Creating matrix of shared classes for " + major

    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

    for cls in classes:
        cls_pos = class_table[cls]
        cursor.execute("SELECT DISTINCT Identifier FROM complete_enrollment_data WHERE Subject = %s AND Major1 = %s", (cls, major))
        students = [student[0] for student in cursor.fetchall()]

        for student in students:
            cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data WHERE Identifier = %s", (student,))
            subjects = [subject[0] for subject in cursor.fetchall()]
            
            for subject in subjects:    # subjects are the classes that student has taken
                matrix[cls_pos][class_table[subject]] += 1     # goes down column, then across the row


    # output matrix to CSV
    # print "Outputting..."
    # with open("test_classes_popularity.csv", "wb") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(matrix)


    """ Insert to database using psycopg2
    http://initd.org/psycopg/docs/usage.html """

    print "Inserting..."
    cursor.execute("INSERT INTO shared_classes_by_major (MAJOR, MATRIX) VALUES (%s, %s)", (major.strip(), matrix))
    conn.commit()
