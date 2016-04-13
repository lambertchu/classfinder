from django.conf.urls import url

from . import views

app_name = 'recommender'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^recommendations/$', views.recommendations, name='recommendations'),
    url(r'^major/$', views.popular_classes_by_major, name='major'),
    url(r'^subject/$', views.subject_info, name='subject_info'),
    url(r'^subject/(?P<response>\w+\.\w+)/$', views.subject_info, name='subject_info'),
]