from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .forms import GetRecsForm, GetPopularClassesForm, GetSubjectForm


def index(request):
    return render(request, 'recommender/index.html')


def recommendations(request):
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


            recs = generate_recs.generate_recommendations(major, cur_sem, classes, keywords)
            # recs = generate_recs.generate_recommendations_by_similarity(major, cur_sem, classes, keywords)
            # recs = generate_recs.generate_recommendations_by_importance(major, cur_sem, classes, keywords)
            # recs = generate_recs.keyword_similarity(keywords)

            return render(request, 'recommender/recommendations.html', {'recs':recs[0:50]})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetRecsForm()

    return render(request, 'recommender/form.html', {'form': form})


def popular_classes_by_major(request):
    import popular_classes_by_major
    import create_graphs

    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = GetPopularClassesForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            major = form.cleaned_data['major']
            term = form.cleaned_data['semester']
            classes = popular_classes_by_major.get_most_popular_classes(major, term)


            # Create horizontal bar graph
            data = create_graphs.create_horizontal_bar_graph(major, term, classes)
            return render(request, 'recommender/classes_by_major.html', data)


    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetPopularClassesForm()

    return render(request, 'recommender/form.html', {'form': form})


def subject_info(request, response=None):
    import subject_info
    import create_graphs

    form = GetSubjectForm()
    if request.method == 'POST':
        form = GetSubjectForm(request.POST)

        if form.is_valid():
            response = form.cleaned_data['subject']

    if response == None:
        return render(request, 'recommender/subject_info_page.html', {'form': form})

    info = subject_info.get_online_info(response)
    if info == None:
        # TODO: only do this for English words. Invalid classes should throw error
        import keyword_similarity
        results = keyword_similarity.keyword_similarity(response)
        return render(request, 'recommender/subject_search_results.html', {'results': results})

    term_stats = subject_info.get_term_stats(response)

    # Create bar graph
    data = create_graphs.create_bar_graph(term_stats, form, response, info)
    return render(request, 'recommender/subject_info_page.html', data)
