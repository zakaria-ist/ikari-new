from django.conf.urls import url
from countries import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='country_list'),
    url(r'^all/$', views.list_country, name='list_country'),
    url(r'^add/(?P<menu_type>\d+)/$', views.country_add, name='country_add'),
    url(r'^edit/(?P<country_id>\d+)/(?P<menu_type>\d+)/$', views.country_edit, name='country_edit'),
    url(r'^delete/(?P<country_id>\d+)/$', views.country_delete, name='country_delete'),
    url(r'^list/pagination$', views.Countries__asJson, name='Countries__asJson'),
    url(r'^country_list/$', views.country_list_asJson, name='country_list_asJson'),

]