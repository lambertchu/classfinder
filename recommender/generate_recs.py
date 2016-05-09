import math
from django.core.cache import cache
from django.db.models import Q
from models import CompleteEnrollmentData, SharedClassesByMajor, SubjectInfo
import get_new_classes


"""
Create a matrix that records the number of students that took each pair of classes
"""
def create_shared_classes_table(major, all_classes, class_table):
    num_classes = len(all_classes)
    pairs = CompleteEnrollmentData.objects.filter(Q(major1=major) | Q(major2=major)).values_list("identifier","subject")
    # Only work with students declared in the given major

    # Create dictionary mapping each student to a list of classes taken
    student_class_dict = {}
    for identifier, cls in pairs:
        if identifier not in student_class_dict and cls in all_classes:
            student_class_dict[identifier] = [cls]
        elif cls in all_classes:
            student_class_dict[identifier].append(cls)

    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]
    for student, classes in student_class_dict.iteritems():
        for sc1 in classes:
            for sc2 in classes:
                matrix[class_table[sc1]][class_table[sc2]] += 1

    return matrix


"""
Determine the likelihood of a class being taken given the current term.
"""
def get_term_relevance_data(cur_term, new_classes):
    try:
        subject_info = SubjectInfo.objects.filter(subject__in=new_classes).values("subject", "title", cur_term, "total")
    except:
        print "Error connecting to SubjectInfo database table."

    term_data = {}
    class_titles = {}
    for row in subject_info:
        subject = row["subject"]
        class_titles[subject] = row["title"]

        cur_term_count = row[cur_term] + 1
        total_count = row["total"] + 16
        time_modifier = float(cur_term_count) / total_count
        term_data[subject] = time_modifier
        
    return term_data, class_titles


"""
Calculate the "importance" rating of one new class
"""
def calculate_rating(new_class, student_classes_list, class_table, shared_classes_table):
    rating = 1
    for s in student_classes_list:
        index = class_table[s]
        total_number_class = shared_classes_table[index][index]
        if total_number_class == 0:
            break

        try:
            shared_number = int(shared_classes_table[class_table[new_class]][index])
            rating *= math.exp(0.5 * shared_number / total_number_class)
        except:
            print (new_class, s)

    return rating


"""
Generate recommendations for a given student using the "importance" method.
Recommendations are for the current semester and are based upon all classes taken by the student.

TODO: error handling for invalid class?
"""
def generate_recommendations(major, cur_semester, student_classes):
    student_classes_list = student_classes.split()
    new_classes = get_new_classes.get_classes_to_take(major, student_classes)
    all_classes = student_classes_list + new_classes
    
    major = major.replace('_', ' ')
    class_table = {k:v for k, v in zip(all_classes, xrange(len(all_classes)))}
    shared_classes_table = create_shared_classes_table(major, all_classes, class_table)     # consider caching


    # Calculate time (semester) relevance
    cur_term = "term%s" % cur_semester
    term_data, class_titles = get_term_relevance_data(cur_term, new_classes)


    # Calculate "importance" of each class that hasn't been taken by the student
    importance_ratings = {}

    for new_class in new_classes:
        rating = calculate_rating(new_class, student_classes_list, class_table, shared_classes_table)
        # try:
        #     rating *= term_data[new_class]    # time relevance
        # except:
        #     pass
        importance_ratings[new_class] = rating

    # Create list of classes in order of popularity
    sorted_classes = sorted(importance_ratings, key=importance_ratings.get, reverse=True)

    recs = []
    for c in sorted_classes[:20]:
        try:
            title = class_titles[c]
        except:
            title = ""

        recs.append((c, title))

    return recs
