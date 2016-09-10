import json
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import UserProfile
from .forms import UserForm, UserProfileForm, KeywordsForm, GetPopularClassesForm, GetSubjectForm
import generate_recs, keyword_similarity, subject_info, create_graphs, startup


@login_required
def profile(request):
    mit_classes = startup.mit_classes
    profile = request.user.userprofile
    classes_taken = profile.classes

    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        try:
            form = UserProfileForm(request.POST, instance=request.user.userprofile)
        except:
            print "Couldn't load user profile"
            form = UserProfileForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            profile = form.save(commit=False)
            profile.classes = dict(request.POST.lists())['classes']
            profile.save()
            print form
            return render(request, 'recommender/profile.html', {'form': form, 'mit_classes': mit_classes, 'classes_taken': profile.classes})

    else:
        data = {'major_1':profile.major_1, 'major_2':profile.major_2, 'semester':profile.semester, 'classes':classes_taken}
        form = UserProfileForm(initial=data)
    
    return render(request, 'recommender/profile.html', {'form': form, 'mit_classes': mit_classes, 'classes_taken': classes_taken})


@login_required
def recommendations(request, major):
    #  Choices are: classes, id, major1, major2, semester, user, user_id
    profile = request.user.userprofile

    major1 = profile.major_1
    major2 = profile.major_2
    cur_sem = profile.semester
    classes = profile.classes

    if major1 == None or cur_sem == None or classes == None:
        return redirect(reverse('recommender:profile'))

    if major == "" or major == None:
        major = major1
        
    recs = generate_recs.generate_recommendations(major, cur_sem, classes)

    return render(request, 'recommender/recommendations.html', {'recs':recs, 'major1':major1, 'major2':major2})


# @login_required
# def recommendations_by_keywords(request):
#     form = KeywordsForm()
#     if request.method == 'POST':
#         form = KeywordsForm(request.POST)
#         if form.is_valid():
#             keywords = form.cleaned_data['keywords']
#             results = keyword_similarity.keyword_similarity(keywords)
#             return render(request, 'recommender/recommendations-keywords.html', {'results': results})

#     else:
#         return render(request, 'recommender/recommendations-keywords.html', {'form': form})


@login_required
def popular_classes_by_major(request, classes=None):
    import popular_classes_by_major

    # Display textbox for user to enter a major
    form = GetPopularClassesForm()
    if request.method == 'POST':
        form = GetPopularClassesForm(request.POST)
        if form.is_valid():
            major = form.cleaned_data['major']
            major = str(major.replace('_', ' '))
            term = form.cleaned_data['semester']
            classes = popular_classes_by_major.get_most_popular_classes(major, term)

    # This is the user's first time on the page
    if classes == None:
        return render(request, 'recommender/stats_by_major.html', {'form': form})

    # Create horizontal bar graph
    data = create_graphs.create_horizontal_bar_graph(major, term, classes)
    data['form'] = form
    return render(request, 'recommender/stats_by_major.html', data)


@login_required
def class_info_initial(request):
    # Display textbox for user to enter a class
    form = GetSubjectForm()

    if request.method == 'POST':
        form = GetSubjectForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_']
            return class_info(request, class_name)

    return render(request, 'recommender/stats_by_class.html', {'form': form})


@login_required
def class_info(request, class_name):
    # Display textbox for user to enter a class
    form = GetSubjectForm()
    if request.method == 'POST':
        form = GetSubjectForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_']

    info = subject_info.get_online_info(class_name)


    # The user searched with a keyword
    if info == None:
        # TODO: only do this for English words. Invalid classes should throw error
        recs = keyword_similarity.keyword_similarity(class_name)
        return render(request, 'recommender/recommendations-keywords.html', {'form':form, 'recs': recs})


    # The user searched with a class number
    term_stats = subject_info.get_term_stats(class_name)

    # Create bar graph
    data = create_graphs.create_bar_graph(term_stats, class_name, info)
    data['form'] = form

    # TODO
    # return redirect(reverse('recommender:class_info'), args=(response,), urllib.urlencode(data))
    return render(request, 'recommender/stats_by_class.html', data)


def register(request):
    context = RequestContext(request)
    username = startup.username

    user = User.objects.create_user(username, startup.email, '')
    user.save()
    profile = UserProfile.objects.create(user=user, major1="1_A", major2="None", semester=1)
    profile.save()

    if user.is_active:
        # If the account is valid and active, we can log the user in.
        # We'll send the user back to the homepage.
        user = authenticate(username=username, password='')
        login(request, user)

    # Render the template depending on the context.
    return redirect(reverse('recommender:profile'))


def user_login(request):
    if startup.email == None:
        try:
            # startup.email = request.META['USER']
            startup.email = request.META['SSL_CLIENT_S_DN_Email']
            startup.username = startup.email.split('@')[0]
        except:
            print "Error processing email address."

    context = RequestContext(request)

    username = startup.username

    # Use Django's machinery to attempt to see if the username/password
    # combination is valid - a User object is returned if it is.
    user = authenticate(username=username, password='')

    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
    if user:
        # Is the account active? It could have been disabled.
        if user.is_active:
            # If the account is valid and active, we can log the user in.
            # We'll send the user back to the homepage.
            login(request, user)
            return redirect(reverse('recommender:profile'))
        else:
            # An inactive account was used - no logging in!
            return HttpResponse("Your account is disabled.")
    else:
        return register(request)
