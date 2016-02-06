from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import InfoForm
import generate_recs

"""
def index(request):
	info = models.SubjectInfo.objects.filter(subject='18.01A')
	dictionary = info.values
	return render(request, 'recommender/rec_list.html', {'dictionary':dictionary})		# info.values_list
"""

def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InfoForm(request.POST)
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            

            # redirect to a new URL:
            return HttpResponseRedirect('results/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InfoForm()

    return render(request, 'recommender/form.html', {'form': form})


def results(request):
	return render(request, 'recommender/form.html', {'form': form})