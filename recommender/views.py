from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .forms import GetRecsForm, GetPopularClassesForm


#def index(request):



def get_recommendations(request):
    import generate_recs

    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = GetRecsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            major = form.cleaned_data['major']
            cur_sem = form.cleaned_data['current_semester']
            classes = form.cleaned_data['classes']
            keywords = form.cleaned_data['keywords']

            recs = generate_recs.generate_recommendations_by_similarity(major, cur_sem, classes, keywords)
            # recs = generate_recs.generate_recommendations_by_importance(major, cur_sem, classes, keywords)
            # recs = generate_recs.keyword_similarity(keywords)

            return render(request, 'recommender/recommendations.html', {'recs':recs[0:20]})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetRecsForm()

    return render(request, 'recommender/form.html', {'form': form})


def get_popular_classes_by_major(request):
    import popular_classes_by_major

    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = GetPopularClassesForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            major = form.cleaned_data['major']
            term = form.cleaned_data['current_semester']

            classes = popular_classes_by_major.get_most_popular_classes(major, term)

            return render(request, 'recommender/classes_by_major.html', {'classes':classes})
        # if a GET (or any other method) we'll create a blank form
    
    else:
        form = GetPopularClassesForm()

    return render(request, 'recommender/form.html', {'form': form})


def index(request):
    import subject_info

    subject = '6.006'
    info = subject_info.get_online_info(subject)
    term_stats = subject_info.get_term_stats(subject)
    return render(request, 'recommender/subject_info_page.html', {'subject':subject, 'info':info, 'term_stats':term_stats})


def results(request):
	return render(request, 'recommender/results.html')