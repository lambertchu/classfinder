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
import generate_recommendations

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


# get first X students - we should make this a parameter for the program
cursor.execute("SELECT DISTINCT Identifier FROM enrollment_data_updated WHERE Identifier <= 10001100")
target_students = [s[0] for s in cursor.fetchall()]
print target_students


"""
Get number of terms that a given student has enrolled in
"""
def get_terms(student):
    #cursor = get_database_conn()
    cursor.execute("SELECT DISTINCT Term_Number FROM enrollment_data_updated WHERE Identifier = %s", (student,))
    terms = sorted([term[0] for term in cursor.fetchall()])
    return terms


"""
Calculate error of recommendations for one student
Only applicable for recommendations of 2nd through last terms
"""
def calc_error(student, terms, class_rankings_by_term):
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

            # error_factor = (rank of class - total classes taken) / size of the universe
            factor = max(0, (float(rank) - num_subjects) / (num_classes - num_subjects))

            error += factor

        # find the average error for that student's term
        error /= num_subjects
        term_errors.append(error)

    return term_errors


if __name__ == "__main__":
    #with open("cv_errors_first_100_normalized.csv", "wb") as f:
    with open("TEST.csv", "wb") as f:
        writer = csv.writer(f)
        
        for student in target_students:
            writer.writerow([student])

            terms = get_terms(student)
            writer.writerow(terms[1:])

            class_rankings_by_term = generate_recommendations.generate_recommendations_by_importance(student, terms)

            writer.writerow(calc_error(student, terms, class_rankings_by_term))
            writer.writerow([])
    sys.exit()