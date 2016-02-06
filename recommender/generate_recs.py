import math
from models import CompleteEnrollmentData, SharedClassesByMajor, SubjectInfo

"""
Generate recommendations for a given student using the "importance" methodology.
Recommendations are for EVERY term that the student was enrolled in.
"""
def generate_recommendations_by_importance(major, student_classes, keywords):
    shared_classes_table = get_shared_classes_by_major(major)
    totals = create_totals_table(shared_classes_table)

    # Calculate "importance" of each class that hasn't been taken by the student
    importance_ratings = {}
    for cl in classes:
        total = 1
        for s in student_classes:
            if cl not in student_classes:
                total_number_class = totals[s]
                shared_number = int(shared_classes_table[class_table[cl]][class_table[s]])
                
                if total_number_class != 0:
                    total *= math.exp(0.5 * shared_number / total_number_class)

        # TODO: include other modifiers here, i.e. time relevance and keyword match

            else:
                break

        importance_ratings[cl] = total       # record total for this class


    sorted_importance_ratings = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
    print sorted_importance_ratings[0:9]    # prints top 10 recommendations
    
    return sorted_importance_ratings


"""
Get matrix from database
"""
def get_shared_classes_by_major(m):
    return SharedClassesByMajor.objects.filter(major=m).values_list('matrix', flat=True)[0]


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
classes = CompleteEnrollmentData.objects.order_by().values_list('subject', flat=True).distinct()
num_classes = len(classes)

# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}
