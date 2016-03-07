import math
from django.core.cache import cache
from models import CompleteEnrollmentData, SharedClassesByMajor, SubjectInfo
from gensim.models import Word2Vec


"""
Generate recommendations for a given student using the "importance" method.
Recommendations are for the current semester and are based upon all classes taken by the student.

TODO: error handling for invalid class?
TODO: some classes renamed (i.e. 18.440 to 18.600)
"""
def generate_recommendations_by_importance(maj, cur_semester, student_classes, keywords, term_relevance = False):
    try:
        # NOTE: cached result must be changed when the student changes majors
        shared_classes_table = cache.get('shared_classes_table')
        if shared_classes_table == None:
            shared_classes_table = SharedClassesByMajor.objects.filter(major=maj).values_list("matrix", flat=True)[0]
            #cache.add('shared_classes_table', shared_classes_table, 300)    # store in cache
    except:
        print "Error loading shared_classes_table"

    student_classes_list = student_classes.split()
    new_classes = [x for x in classes if x not in student_classes_list]
    cur_term = "term%s" % cur_semester
    
    totals = create_totals_table(shared_classes_table)
    term_data = get_term_relevance_data(cur_term)       # SHOULD BE CACHED


    # Calculate "importance" of each class that hasn't been taken by the student
    importance_ratings = {}
    for cl in new_classes:
        total = 1
        for s in student_classes_list:
            total_number_class = totals[s]
            if total_number_class == 0:
                break

            try:
                shared_number = int(shared_classes_table[class_table[cl]][class_table[s]])
                total *= math.exp(0.5 * shared_number / total_number_class)
            except:
                print (cl, s)


            # Term relevance
            if term_relevance:
                try:
                    tr_multiplier = term_data[cl]
                    total *= tr_multiplier
                except:
                    continue


            # Keyword match
            if len(keywords) > 0:
                try:
                    class_keywords = SubjectInfo.objects.filter(subject=cl).values_list("keywords", flat=True)[0]
                except:
                    continue

                if len(class_keywords) > 0:
                    sim_rating = w2v_model.n_similarity(class_keywords, keywords.split())
                    total *= sim_rating
                else:
                    total *= .1


        importance_ratings[cl] = total       # record total for this class

    sorted_importance_ratings = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
    return sorted_importance_ratings



"""
Generate recommendations for a given student using the "similarity/Amazon" method.
Recommendations are for the current semester and are based upon all classes taken by the student.
"""
def generate_recommendations_by_similarity(maj, cur_semester, student_classes, keywords, term_relevance = False):
    from scipy import spatial
    try:
        # NOTE: cached result must be changed when the student changes majors
        shared_classes_table = cache.get('shared_classes_table')
        if shared_classes_table == None:
            shared_classes_table = SharedClassesByMajor.objects.filter(major=maj).values_list("matrix", flat=True)[0]
            #cache.add('shared_classes_table', shared_classes_table, 300)    # store in cache
    except:
        print "Error loading shared_classes_table"

    cur_term = "term%s" % cur_semester
    MAJOR_TRIM = '6.'

    student_classes_list = [str(x) for x in student_classes.split()]
    relevant_classes = [str(x) for x in classes if (str(x).startswith(MAJOR_TRIM) or str(x) in student_classes_list)]
    num_rel_classes = len(relevant_classes)

    # Create hash table with keys = classes and values = index in list
    class_table = {k:v for k, v in zip(relevant_classes, xrange(num_rel_classes))}

    # Create nxn similarity table
    similarity_table = [[0 for x in xrange(num_rel_classes)] for y in xrange(num_rel_classes)]

    # Populate similarity_table with the similarity rating between each pair of classes
    for cls in relevant_classes:
        cls_pos = class_table[cls]
        for c in relevant_classes:
            # compute similarity between cls and c
            cls_list = shared_classes_table[cls_pos]
            c_list = shared_classes_table[class_table[c]]
            
            if sum(cls_list) == 0 or sum(c_list) == 0:
                similarity = 0
            else:
                similarity = spatial.distance.cosine(cls_list, c_list)  # CONSIDER PEARSON INSTEAD!

            similarity_table[cls_pos][class_table[c]] = similarity

    # Populate a dictionary mapping each class to its rating
    ratings = {}
    for cls in relevant_classes:
        ratings[cls] = 0

    for cls in student_classes_list:
        cls_pos = class_table[cls]
        row = similarity_table[cls_pos]

        i = 0
        for c in relevant_classes:
            ratings[c] += similarity_table[cls_pos][i]
            i += 1

    sorted_ratings = sorted(ratings, key=ratings.get, reverse=True)
    for i in sorted_ratings[0:20]:
        print ratings[i]
    return sorted_ratings


"""
Determine the likelihood of a class being taken given the current term.
"""
def get_term_relevance_data(cur_term):
    try:
        subject_info = SubjectInfo.objects.values("subject", cur_term, "total")     # maybe also "title"?
    except:
        print "Error"   # need better error handling

    term_data = {}
    for sub in subject_info:
        cur_term_count = sub[cur_term] + 1
        total_count = sub["total"] + 16
        time_modifier = float(cur_term_count) / total_count
        term_data[sub["subject"]] = time_modifier
        
    return term_data


"""
Find classes that are most similar to the given keywords
"""
def keyword_similarity(keywords):
    sim_ratings = {}
    for cl in classes:
        try:
            class_keywords = SubjectInfo.objects.filter(subject=cl).values_list("keywords", flat=True)[0]
        except:
            continue

        if len(class_keywords) == 0:
            sim_ratings[cl] = 0

        else:
            sim_rating = w2v_model.n_similarity(class_keywords, keywords.split())
            sim_ratings[cl] = sim_rating

    # sort and return
    sorted_sim_ratings = sorted(sim_ratings, key=sim_ratings.get, reverse=True)
    return sorted_sim_ratings



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
try:
    classes = CompleteEnrollmentData.objects.order_by().values_list("subject", flat=True).distinct()
except:
    print "Error loading classes"

num_classes = len(classes)

# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}


# # Load Word2Vec model for keyword matching
# try:
#     w2v_model = cache.get('word2vec_model')
#     if w2v_model == None:
#         w2v_model = Word2Vec.load_word2vec_format('/Users/lambertchu/Documents/MIT/SuperUROP/NLP_Data/GoogleNews-vectors-negative300.bin', binary=True)
#         #cache.add('word2vec_model', w2v_model, 600)    # store in cache
# except:
#     print "Error loading Word2Vec model"
