from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views import generic

from models import UserProfile
from .forms import UserForm, UserProfileForm, KeywordsForm, GetPopularClassesForm, GetSubjectForm
import generate_recs, keyword_similarity, subject_info, create_graphs
from dal import autocomplete



# IDEA: create a poll/forum where users can vote for "unknown" classes they recommend



def index(request):
    return render(request, 'recommender/index.html')


@login_required
def profile(request):
    # process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        try:
            form = UserProfileForm(request.POST, instance=request.user.userprofile)
        except:
            form = UserProfileForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            return render(request, 'recommender/profile.html', {'form': form})

    else:
        profile = request.user.userprofile
        data = {'major1':profile.major1, 'major2':profile.major2, 'semester':profile.semester, 'classes':profile.classes}
        form = UserProfileForm(initial=data)

    return render(request, 'recommender/profile.html', {'form': form})


@login_required
def recommendations(request, major):
    #  Choices are: classes, id, major1, major2, semester, user, user_id
    profile = request.user.userprofile
    # return redirect(reverse('recommender:profile'))

    major1 = profile.major1
    major2 = profile.major2
    cur_sem = profile.semester
    classes = profile.classes

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
    data = create_graphs.create_horizontal_bar_graph(major, form, term, classes)
    return render(request, 'recommender/stats_by_major.html', data)


@login_required
def class_info_initial(request):
    # Display textbox for user to enter a class
    form = GetSubjectForm()

    if request.method == 'POST':
        form = GetSubjectForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            return class_info(request, class_name)

    return render(request, 'recommender/stats_by_class.html', {'form': form})


@login_required
def class_info(request, class_name):
    # Display textbox for user to enter a class
    form = GetSubjectForm()
    if request.method == 'POST':
        form = GetSubjectForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_name']

    info = subject_info.get_online_info(class_name)


    # The user searched with a keyword
    if info == None:
        # TODO: only do this for English words. Invalid classes should throw error
        recs = keyword_similarity.keyword_similarity(class_name)
        return render(request, 'recommender/recommendations-keywords.html', {'form':form, 'recs': recs})


    # The user searched with a class number
    term_stats = subject_info.get_term_stats(class_name)

    # Create bar graph
    data = create_graphs.create_bar_graph(term_stats, form, class_name, info)

    # TODO
    # return redirect(reverse('recommender:class_info'), args=(response,), urllib.urlencode(data))
    return render(request, 'recommender/stats_by_class.html', data)


def register(request):
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'registration/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)


def user_login(request):
    context = RequestContext(request)
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return render_to_response('recommender/index.html')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('registration/login.html', {}, context)


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # TODO: message that says "Thanks for using"
    # Take the user back to the homepage.
    return render(request, 'recommender/index.html')





# from select2_many_to_many.forms import TestForm
# from select2_many_to_many.models import TestModel
# # from models import SubjectInfo


# class UpdateView(generic.UpdateView):
#     model = TestModel
#     form_class = TestForm
#     template_name = 'recommender/select2_outside_admin.html'
#     success_url = reverse_lazy('select2_outside_admin')

#     def get_object(self):
#         return TestModel.objects.first()

