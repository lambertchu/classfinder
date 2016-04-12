import string
import subject_info
from gensim.models import Word2Vec
from models import CompleteEnrollmentData


"""
Find classes that are most similar to the given keywords
"""
def keyword_similarity(keywords):
    stop_list = set('for a of also by the and to in on as at from with but how about such eg ie'.split())   # remove common words
    sim_ratings = {}
    for cl in mit_classes:
        try:
            words = SubjectInfo.objects.filter(subject=cl).values_list("keywords", flat=True)[0]
            class_keywords = [x for x in words if x not in stop_list]
        except:
            sim_ratings[cl] = 0
            continue

        if len(class_keywords) == 0:
            sim_ratings[cl] = 0
            continue

        # Get title of class
        title_list = SubjectInfo.objects.filter(subject=cl).values_list("title", flat=True)[0].split()
        title_keywords = [x for x in title_list if x not in stop_list]

        keywords_list = keywords.split()
        sim_rating = w2v_model.n_similarity(class_keywords, keywords_list)
        try:
            sim_rating += 2*w2v_model.n_similarity(title_keywords, keywords_list)
        except:
            print cl
        sim_ratings[cl] = sim_rating

    # sort and return
    sorted_sim_ratings = sorted(sim_ratings, key=sim_ratings.get, reverse=True)
    return sorted_sim_ratings



"""
The following is executed upon import
"""
# Get list of all classes
try:
    classes = CompleteEnrollmentData.objects.order_by().values_list("subject", flat=True).distinct()
except:
    print "Error loading classes"

mit_classes = []
for cl in classes:
    if cl == None or cl[0:2] == "HA" or cl[0:2] == "MC" or (cl[0:1] == "W" and cl[0:3] != "WGS"):
        continue
    mit_classes.append(cl)


# # Load Word2Vec model for keyword matching
# try:
#     w2v_model = cache.get('word2vec_model')
#     if w2v_model == None:
w2v_model = Word2Vec.load_word2vec_format('/Users/lambertchu/Documents/MIT/SuperUROP/NLP_Data/GoogleNews-vectors-negative300.bin', binary=True)
#         #cache.add('word2vec_model', w2v_model, 600)    # store in cache
# except:
#     print "Error loading Word2Vec model"