from django.conf.urls import url

from . import views
from models import UserProfile
from dal import autocomplete

app_name = 'recommender'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^recommendations/$', views.recommendations, name='recommendations'),
    url(r'^recommendations-keywords/$', views.recommendations_by_keywords, name='keywords'),
    url(r'^major/$', views.popular_classes_by_major, name='major'),
    url(r'^subject/$', views.subject_info, name='subject_info'),
    url(r'^subject/(?P<response>\w+\.\w+)/$', views.subject_info, name='subject_info'),
    url( r'^classes-autocomplete/$', views.UpdateView.as_view(), name='classes-autocomplete', ),
]