from django.shortcuts import render
from django.core.urlresolvers import reverse
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
    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InfoForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            major = form.cleaned_data['major']
            cur_sem = form.cleaned_data['current_semester']
            classes = form.cleaned_data['classes']
            keywords = form.cleaned_data['keywords']

            recs = generate_recs.generate_recommendations_by_importance(major, cur_sem, classes, keywords)

            return render(request, 'recommender/results.html', {'recs':recs[0:20]})
            #return HttpResponseRedirect(reverse('recommender:results', args=recs[0:20],))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InfoForm()

    return render(request, 'recommender/form.html', {'form': form})


def results(request):
	return render(request, 'recommender/results.html')