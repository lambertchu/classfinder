from django.db.models import Q
from models import CompleteEnrollmentData, SubjectInfo


"""
Get the most popular classes taken by students of the given major in the given term
"""
def get_most_popular_classes(major, term):
	subjects = CompleteEnrollmentData.objects.filter(Q(term_number=term) & (Q(major1=major) | Q(major2=major))).values_list("subject", flat=True)
	subjects_dict = {}

	for subject in subjects:
		if subject not in subjects_dict:
			subjects_dict[subject] = 1
		else:
			subjects_dict[subject] += 1

	sorted_subjects = sorted(subjects_dict, key=subjects_dict.get, reverse=True)

	classes = []
	num_on_page = 20
	for subject in sorted_subjects[0:num_on_page]:
		try:
			title = SubjectInfo.objects.filter(subject=subject).values_list("title", flat=True)[0]
		except:
			title = None
		info = (str(subject), str(title), subjects_dict[subject])
		classes.append(info)

	return classes