from recommender.models import CompleteEnrollmentData
# from gensim.models import Word2Vec
# model = Word2Vec.load_word2vec_format('recommender/static/recommender/GoogleNews-vectors-negative300.bin', binary=True)


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
mit_classes.sort()

email = None
username = None

# TODO: filter classes that were rarely taken and/or not offered anymore
# Need to fix Subject_Info table. Some classes have missing info - fill in the blanks.
# Some classes not included at all - use the missing classes from keyword search to find those classes