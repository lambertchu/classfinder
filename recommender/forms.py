from django import forms

class InfoForm(forms.Form):
    major = forms.CharField(max_length=256)
    classes = forms.CharField(max_length=256)
    keywords = forms.CharField(max_length=256)