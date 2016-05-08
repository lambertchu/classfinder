from django.conf.urls import url

from . import views
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
    url(r'^class/$', views.class_info, name='class_info'),
    url(r'^class/(?P<response>\w+\.\w+)/$', views.class_info, name='class_info'),
    # url( r'^classes-autocomplete/$', views.UpdateView.as_view(), name='classes-autocomplete', ),
    # url( r'test/$', views.UpdateView.as_view(), name='select2_outside_admin', ),
]