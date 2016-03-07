from django import forms

class GetRecsForm(forms.Form):
    major = forms.CharField(max_length=256)
    current_semester = forms.ChoiceField(choices=[(x, x) for x in range(1, 17)])
    classes = forms.CharField(max_length=256)
    keywords = forms.CharField(max_length=256, required=False)


class GetPopularClassesForm(forms.Form):
	major = forms.CharField(max_length=256)
	current_semester = forms.ChoiceField(choices=[(x, x) for x in range(1, 17)])