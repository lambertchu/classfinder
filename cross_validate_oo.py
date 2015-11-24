# calculate i2i CF for the first 800 students
# for each of the remaining 200 students
#   reveal one more semester
#       find new classes that are most similar to those already taken
#       recommend the top X for next semester
#       calculate coverage & accuracy based upon S (selected next semester) and R (recommended)

# TODO: fix initial file read

import sys
import math
import csv
import psycopg2
from scipy import spatial

def get_database_conn():
    try:
        with open('pass.txt', 'r') as f:
            password = f.readline()
        conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
    except:
        print "Unable to connect to the database"
        sys.exit()

    # conn.cursor will return a cursor object that you can use to perform queries
    return conn.cursor()


"""
Get list of all classes
"""
def get_all_classes():
    cursor = get_database_conn()
    cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated")
    classes = [cl[0] for cl in cursor.fetchall()]
    #num_classes = len(classes)
    return classes


"""
Create hash table with keys = classes and values = index in list
"""
def create_class_table():
    classes = get_all_classes()
    return {k:v for k, v in zip(classes, xrange(len(classes)))}


"""
create 2D list with number of students that took each pair of classes
NOTE: we should re-create this file with the class names in the header
      and use that info to create the shared_classes_table
    Maybe we should do this first, then create the list of classes and hash table
"""
def create_shared_classes_table():
    with open('output_matrix_updated.csv', 'r') as f:
        reader = csv.reader(f)
        return list(reader)


"""
Create hash table for total number of students that took each class
"""
def create_totals_table(classes, shared_classes_table):
    totals = {}
    count = 0
    for row in shared_classes_table:
        row_num = [int(x) for x in row]
        totals[classes[count]] = sum(row_num)
        count += 1
    return totals


"""
Get number of terms taken by a student
"""
def get_terms(student):
    cursor = get_database_conn()
    cursor.execute("SELECT DISTINCT Term_Number FROM enrollment_data_updated WHERE Identifier = %s", (student,))
    terms = sorted([term[0] for term in cursor.fetchall()])
    return terms

def make_recommendations():
    cursor = get_database_conn()
    # get last X students - we should make this a parameter for the script
    #cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated") # WHERE Identifier = ...
    #students = [student[0] for student in cursor.fetchall()]
    students = ["10001010"]

    classes = get_all_classes()
    class_table = create_class_table()
    shared_classes_table = create_shared_classes_table()
    totals = create_totals_table(classes, shared_classes_table)

    # create table: key = term, value = importance ratings of classes for that student
    # used for calculating recommendation ratings
    importance_table = {}


    # create hash table with keys = terms, values = dictionary mapping class to ranking
    # used for calculating errors
    class_rankings_by_term = {}

    for student in students:
        terms = get_terms(student)
        subjects = []

        for term in terms:
            #print term
            cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number = %s", (student,term))
            subjects += [subject[0] for subject in cursor.fetchall()]
            #print subjects

            # calculate "importance" of each class - we exclude current subjects from similarity comparisons
            importance_ratings = {}
            for cl in classes:
                total = 1
                for subject in subjects:
                    if cl not in subjects:
                        shared_number = int(shared_classes_table[class_table[cl]][class_table[subject]])
                        total_number_subject = totals[subject]
                        total *= math.exp(0.5 * shared_number / total_number_subject)
                    else:
                        #print cl
                        break
                importance_ratings[cl] = total       # record total for this class

            importance_table[term] = importance_ratings
            class_rankings_by_term[term] = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
            print class_rankings_by_term[term][0:7]
            
    calc_error(students, class_rankings_by_term)

"""
with open("cross_validation_results.csv", "wb") as f:
    writer = csv.writer(f)
    
    for t in terms:
        writer.writerow([t])
        term_dict = importance_table[t]
        writer.writerow(term_dict.keys())
        term_vals = [term_dict[key] for key in term_dict.keys()]
        writer.writerow(term_vals)
"""

"""
Calculate error of recommendations
Only applicable for recommendations of 2nd through last terms
"""
def calc_error(students, class_rankings_by_term):
    cursor = get_database_conn()

    for student in students:
        print student
        terms = get_terms(student)

        for term in terms[1:]:
            print term
            cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number = %s", (student,term))
            subjects = [subject[0] for subject in cursor.fetchall()]
            num_subjects = len(subjects)
            print subjects

            # error = [\sum_{x in C} max(0, (rank(x)/|C| - 1))] / |C|
            error = 0
            for subject in subjects:
                for i in xrange(0, len(class_rankings_by_term[term-1])):
                    if class_rankings_by_term[term-1][i] == subject:
                        rank = i+1   # rank is not zero-indexed
                        break

                factor = str(max(0, float(rank) / num_subjects - 1))
                print "subject: %s, rank: %s, factor: %s" % (subject, rank, factor)
                error += max(0, float(rank / num_subjects))
            error /= num_subjects
            print "Error of term %s is %s" % (term, error)


if __name__ == "__main__":
    make_recommendations()
    sys.exit()