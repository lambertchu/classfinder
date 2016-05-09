import string
from numpy import log

import startup, subject_info
from models import CompleteEnrollmentData, SubjectInfo


"""
Find classes that are most similar to the given keywords
"""
def keyword_similarity(user_keywords):
    stop_list = set('for a of also by the and to in on as at from with but how about such eg ie'.split())   # remove common words
    sim_ratings = {}
    class_titles = {}

    for cl in startup.mit_classes:
        try:
            words, title = SubjectInfo.objects.filter(subject=cl).values_list("keywords", "title")[0]
        except:
            continue

        class_keywords = [x for x in words if x not in stop_list]
        if len(class_keywords) == 0 or len(title) == 0:
            continue

        class_titles[cl] = title

        # Get each word in title of class
        title_list = title.split()
        title_keywords = [x for x in title_list if x not in stop_list]

        keywords_list = user_keywords.split()
        sim_rating = startup.model.n_similarity(class_keywords, keywords_list)

        try:
            sim_rating += 2*startup.model.n_similarity(title_keywords, keywords_list)
            # sim_rating += log(total)
        except:
            print cl
        sim_ratings[cl] = sim_rating

    # sort and return
    sorted_sim_ratings = sorted(sim_ratings, key=sim_ratings.get, reverse=True)

    recs = []
    for c in sorted_sim_ratings[:20]:
        try:
            title = class_titles[c]
        except:
            title = ""

        recs.append((c, title))

    return recs
