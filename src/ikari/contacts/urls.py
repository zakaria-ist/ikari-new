from django.conf.urls import url
from contacts import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='contact_list'),
    url(r'^add/$', views.contact_add, name='contact_add'),
    url(r'^edit/(?P<contact_id>\d+)/$', views.contact_edit, name='contact_edit'),
    url(r'^delete/(?P<contact_id>.*)/$', views.contact_delete, name='contact_delete'),
    url(r'^refer_add/(?P<contact_type>.*)/(?P<refer_id>.*)/$', views.contact_refer_add, name='contact_refer_add'),
    url(r'^refer_edit/(?P<contact_id>.*)/$', views.contact_refer_edit, name='contact_refer_edit'),
    url(r'^refer_delete/(?P<contact_id>.*)/$', views.contact_refer_delete, name='contact_refer_delete'),
    url(r'^list/pagination$', views.ContactList__asJson, name='ContactList__asJson'),
]
