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

            return render(request, 'recommender/recommendations.html', {'recs':recs[0:20]})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetRecsForm()

    return render(request, 'recommender/form.html', {'form': form})


def popular_classes_by_major(request):
    import popular_classes_by_major

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

            # Create bar graph
            xdata = []
            ydata = []
            for cls in classes:
                xdata.append((cls[0], cls[1]))
                ydata.append(cls[2])

            chartdata = {'x': xdata, 'y': ydata}
            charttype = 'discreteBarChart'
            chartcontainer = 'discretebarchart_container'
            data = {
                'major': major,
                'term': term,
                'charttype': charttype,
                'chartdata': chartdata,
                'chartcontainer': chartcontainer,
                'extra': {
                    'x_is_date': False,
                    'x_axis_format': '',
                    'tag_script_js': True,
                    'jquery_on_ready': False,
                }
            }
            return render(request, 'recommender/classes_by_major.html', data)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = GetPopularClassesForm()

    return render(request, 'recommender/form.html', {'form': form})


def subject_info(request, subject=None):
    import subject_info

    form = GetSubjectForm()
    if request.method == 'POST':
        form = GetSubjectForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data['subject']

    if subject == None:
        return render(request, 'recommender/subject_info_page.html', {'form': form})

    info = subject_info.get_online_info(subject)
    term_stats = subject_info.get_term_stats(subject)

    # Create pie chart
    xdata = []
    ydata = []
    for term, value in term_stats:
        xdata.append(term)
        ydata.append(value)

    chartdata = {'x': xdata, 'y': ydata}
    charttype = 'discreteBarChart'
    chartcontainer = 'discretebarchart_container'
    data = {
        'form': form,
        'subject': subject,
        'info': info,
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render(request, 'recommender/subject_info_page.html', data)
