from django import forms
from django.contrib.auth.models import User
from recommender.models import UserProfile, CompleteEnrollmentData
from dal import autocomplete


"""
Import all majors at MIT. Returns a list of tuples of the majors
"""
def get_mit_majors():
	majors = []
	with open('recommender/static/recommender/majors.txt', 'r') as f:
		content = f.readlines()

	for major in content:
		major = major.rstrip()	# remove trailing newline
		major_space = major.replace('_', '-')
		majors.append((major, major_space))
	return majors


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
	majors = get_mit_majors()
	with open('recommender/static/recommender/semesters.txt', 'r') as f:
		semesters = [tuple(i.split(',')) for i in f]

	major_1 = forms.ChoiceField(choices=majors, initial="None")
	major_2 = forms.ChoiceField(choices=majors, initial="None")
	semester = forms.ChoiceField(choices=semesters)
	#classes_taken = forms.CharField(max_length=256)

	class Meta:
		model = UserProfile
		fields = ('major_1', 'major_2', 'semester')


class GetPopularClassesForm(forms.Form):
	majors = get_mit_majors()
	major = forms.ChoiceField(choices=majors, initial="None")
	semester = forms.ChoiceField(choices=[(x, x) for x in range(1, 17)])


class GetSubjectForm(forms.Form):
	class_ = forms.CharField(max_length=256)	# TODO: divide by course and make dropdowns?


class KeywordsForm(forms.Form):
	keywords = forms.CharField(max_length=256)
