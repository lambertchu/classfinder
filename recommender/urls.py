from django.conf.urls import url
from . import views

app_name = 'recommender'
urlpatterns = [
    url(r'^$', views.user_login, name='index'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^login/$', views.user_login, name='login'),
    # url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^recommendations/(?P<major>)/$', views.recommendations, name='recommendations'),
    url(r'^recommendations/(?P<major>\w+)/$', views.recommendations, name='recommendations'),
    # url(r'^recommendations-keywords/$', views.recommendations_by_keywords, name='keywords'),
    url(r'^major/$', views.popular_classes_by_major, name='major'),
    url(r'^class/$', views.class_info_initial, name='class_info_initial'),
    url(r'^class/(?P<class_name>\w+\.\w+)/$', views.class_info, name='class_info'),
]
