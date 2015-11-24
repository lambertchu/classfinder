# calculate i2i CF for the first 1100 students
# for each of the remaining 100 students
#   reveal one more semester
#       find new classes that are most similar to those already taken
#       recommend the top X for next semester
#       calculate coverage & accuracy based upon S (selected next semester) and R (recommended)


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


# get last X students - we should make this a parameter for the program
cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated WHERE Identifier > 10001100")
target_students = [s[0] for s in cursor.fetchall()]
print target_students


"""
Create 2D list with number of students that took each pair of classes
"""
def create_shared_classes_table(class_table):
    print "Creating matrix of shared classes..."

    # create nxn matrix with n = total number of classes
    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

    for cls in classes:
        cls_pos = class_table[cls]
        cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated WHERE Subject = %s", (cls,))
        students = [student[0] for student in cursor.fetchall()]

        for student in students:
            if student not in target_students:
                cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s", (student,))
                subjects = [subject[0] for subject in cursor.fetchall()]
            
                for subject in subjects:    # subjects are the classes that student has taken
                    matrix[cls_pos][class_table[subject]] += 1     # goes down column, then across the row

    return matrix

"""
Create hash table for total number of students that took each class
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
Get number of terms taken by a student
"""
def get_terms(student):
    #cursor = get_database_conn()
    cursor.execute("SELECT DISTINCT Term_Number FROM enrollment_data_updated WHERE Identifier = %s", (student,))
    terms = sorted([term[0] for term in cursor.fetchall()])
    return terms

def generate_recommendations():
    print "Generating recommendations..."

    # create hash table with keys = classes and values = index in list
    class_table = {k:v for k, v in zip(classes, xrange(num_classes))}

    shared_classes_table = create_shared_classes_table(class_table)
    totals = create_totals_table(shared_classes_table)

    with open("cv_errors.csv", "wb") as f:
        writer = csv.writer(f)

        for student in target_students:
            writer.writerow([student])

            # create table: key = term, value = importance ratings of classes for that student
            # used for calculating recommendation ratings
            importance_table = {}

            # create hash table with keys = terms, values = dictionary mapping class to ranking
            # used for calculating errors
            class_rankings_by_term = {}

            terms = get_terms(student)
            writer.writerow(terms[1:])
            student_classes = []

            for term in terms:
                #print term
                cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number = %s", (student,term))
                student_classes += [c[0] for c in cursor.fetchall()]
                #print subjects

                # calculate "importance" of each class - we exclude current subjects from similarity comparisons
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
                
            writer.writerow(calc_error(student, terms, class_rankings_by_term))
            writer.writerow([])


"""
Calculate error of recommendations for one student
Only applicable for recommendations of 2nd through last terms
"""
def calc_error(student, terms, class_rankings_by_term):
    #print "Calculating error..."
    term_errors = []

    for prev_term, cur_term in zip(terms, terms[1:]):
        cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated WHERE Identifier = %s AND Term_Number = %s", (student, cur_term))
        subjects = [subject[0] for subject in cursor.fetchall()]
        num_subjects = len(subjects)

        # error = [\sum_{x in C} max(0, (rank(x)/|C| - 1))] / |C|
        error = 0
        for subject in subjects:
            for i in xrange(0, len(class_rankings_by_term[prev_term])):
                if class_rankings_by_term[prev_term][i] == subject:
                    rank = i+1   # rank is not zero-indexed
                    break

            factor = max(0, float(rank) / num_subjects - 1)
            #info = "subject: %s, rank: %s, error: %s" % (subject, rank, factor)
            error += factor

        error /= num_subjects
        term_errors.append(error)

    return term_errors


if __name__ == "__main__":
    generate_recommendations()
    sys.exit()