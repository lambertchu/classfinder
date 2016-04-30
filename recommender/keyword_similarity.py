import string
from numpy import log

import subject_info
import startup
from models import CompleteEnrollmentData, SubjectInfo


"""
Find classes that are most similar to the given keywords
"""
def keyword_similarity(keywords):
    stop_list = set('for a of also by the and to in on as at from with but how about such eg ie'.split())   # remove common words
    sim_ratings = {}

    for cl in mit_classes:
        try:
            words, title = SubjectInfo.objects.filter(subject=cl).values_list("keywords", "title")[0]
            class_keywords = [x for x in words if x not in stop_list]
        except:
            continue

        if len(class_keywords) == 0 or len(title) == 0:
            continue

        # Get title of class
        title_list = title.split()
        title_keywords = [x for x in title_list if x not in stop_list]

        keywords_list = keywords.split()
        sim_rating = startup.model.n_similarity(class_keywords, keywords_list)

        try:
            sim_rating += 2*startup.model.n_similarity(title_keywords, keywords_list)
            # sim_rating += log(total)
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
