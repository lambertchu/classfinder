import sys
import math
import csv
import psycopg2
from scipy import spatial


# connect to database
try:
    with open('pass.txt', 'r') as f:
        password = f.readline()
    conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
except:
    print "Unable to connect to the database"
    sys.exit()
# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()


# Get list of all classes
cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated")
classes = [cl[0] for cl in cursor.fetchall()]
num_classes = len(classes)


# create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}


# PROBLEM: excess white spaces in the major1 field
#shared_classes_table = create_shared_classes_table(class_table, "8")
shared_classes_table = create_shared_classes_table(class_table)
totals = create_totals_table(shared_classes_table)


"""
Create 2D list with number of students that took each pair of classes,
such that the students are in the given major
"""
#def create_shared_classes_table(class_table, major):
def create_shared_classes_table(class_table):
    #print "Creating matrix of shared classes for Course %s..." % major
    print "Creating matrix of shared classes"

    # create nxn matrix with n = total number of classes
    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

    for cls in classes:
        cls_pos = class_table[cls]
        #cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated WHERE Subject = %s AND Identifier > 10001100 AND Major_1 = '%s'", (cls,major))
        cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated WHERE Subject = %s AND Identifier > 10001100", (cls,))
        students = [student[0] for student in cursor.fetchall()]

        for student in students:
            cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s", (student,))
            subjects = [subject[0] for subject in cursor.fetchall()]
            
            for subject in subjects:    # subjects are the classes that student has taken
                matrix[cls_pos][class_table[subject]] += 1     # goes down column, then across the row

    return matrix


"""
Create hash table that maps each class to the total number of students enrolled in that class
"""
def create_totals_table(shared_classes_table):
    totals = {}
    count = 0
    for row in shared_classes_table:
        row_num = [int(x) for x in row]
        totals[classes[count]] = sum(row_num)
        count += 1
    return totals


"""
Generate recommendations for a given student using the "importance" methodology.
Recommendations are for EVERY term that the student was enrolled in.
"""
def generate_recommendations_by_importance(student, terms):

    # create table: key = term, value = importance ratings of classes for that student
    # used for calculating recommendation ratings
    importance_table = {}

    # create hash table with keys = terms, values = dictionary mapping class to ranking
    # used for calculating errors
    class_rankings_by_term = {}

    student_classes = []

    for term in terms:
        #print term
        cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number = %s", (student,term))
        student_classes += [c[0] for c in cursor.fetchall()]
        #print subjects

        # calculate "importance" of each class that hasn't been taken by the student
        importance_ratings = {}
        for cl in classes:
            total = 1
            for s in student_classes:
                if cl not in student_classes:
                    shared_number = int(shared_classes_table[class_table[cl]][class_table[s]])
                    total_number_class = totals[s]

                    if total_number_class != 0:
                        total *= math.exp(0.5 * shared_number / total_number_class)

                else:
                    break

            importance_ratings[cl] = total       # record total for this class

        importance_table[term] = importance_ratings
        class_rankings_by_term[term] = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
        #print class_rankings_by_term[term][0:7]    # prints top 8 recommendations
    
    return class_rankings_by_term
                

"""
Goal: generate recommendations using the "similarity" method (i.e. i2i CF)
"""
def generate_recommendations_similarity():

    # create hash table with keys = terms, values = dictionary mapping class to ranking
    # used for calculating errors
    # class_rankings_all_terms = {}

    terms = [4]
    student_classes = []

    for term in terms:
        #print term
        cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number <= %s", (student,term))
        student_classes += [c[0] for c in cursor.fetchall()]
        #print subjects

        # find "similarity" of each class - we exclude current subjects from similarity comparisons
        term_similarity_ratings = {}     # initialiaze similarity of each to 0
        for s in student_classes:
            for cl in classes:
                if cl not in student_classes:
                    pass
                    #term_similarity_ratings[cl] += # get rating from database


        #class_rankings_all_terms[term] = sorted(term_similarity_ratings, key=term_similarity_ratings.get, reverse=True)
        #print class_rankings_all_terms[term][0:7]    # prints top 8 recommendations
