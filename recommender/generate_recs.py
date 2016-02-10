import math
from models import CompleteEnrollmentData, SharedClassesByMajor, SubjectInfo

"""
Generate recommendations for a given student using the "importance" methodology.
Recommendations are for EVERY term that the student was enrolled in.
"""
def generate_recommendations_by_importance(maj, cur_semester, student_classes, keywords):
    student_classes_list = student_classes.split()
    # shared_classes_table = SharedClassesByMajor.objects.filter(major='  10 B   ').values_list('matrix', flat=True)[0]
    # NEED ERROR HANDLING

    totals = create_totals_table(shared_classes_table)

    # Calculate "importance" of each class that hasn't been taken by the student
    importance_ratings = {}
    for cl in classes:
        total = 1
        for s in student_classes_list:
            if cl not in student_classes_list:
                total_number_class = totals[s]
                shared_number = int(shared_classes_table[class_table[cl]][class_table[s]])
                
                if total_number_class != 0:
                    total *= math.exp(0.5 * shared_number / total_number_class)

                # Time Relevance
                cur_term = "term%s" % cur_semester
                try:
                    cur_semester_count = SubjectInfo.objects.filter(subject=cl).values_list(cur_term, flat=True)[0]
                    class_total = SubjectInfo.objects.filter(subject=cl).values_list("total", flat=True)[0]
                except:
                    continue

                time_modifier = float(cur_semester_count) / class_total
                total *= time_modifier

                # Keyword Match

            else:
                break

        importance_ratings[cl] = total       # record total for this class

    sorted_importance_ratings = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
    return sorted_importance_ratings


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
The following is executed upon import
"""
# Get list of all classes
# NEED ERROR HANDLING
cls = CompleteEnrollmentData.objects.order_by().values_list('subject', flat=True).distinct()
num_classes = len(cls)
classes = [c.strip() for c in cls]

shared_classes_table = SharedClassesByMajor.objects.filter(major='  10 B   ').values_list('matrix', flat=True)[0]

# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}
