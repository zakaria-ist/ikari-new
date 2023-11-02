from django.conf.urls import url
from transactions import views

urlpatterns = [
    url(r'^$', views.trans_method_list, name='index'),
    url(r'^method/list/$', views.trans_method_list, name='trans_method_list'),
    url(r'^method/all/$', views.trans_mode, name='trans_mode'),
    url(r'^method/add/(?P<menu_type>.*)/$', views.trans_method_add, name='trans_method_add'),
    url(r'^method/edit/(?P<trans_method_id>.*)/(?P<menu_type>.*)/$', views.trans_method_edit, name='trans_method_edit'),
    url(r'^method/delete/(?P<trans_method_id>\d+)/$', views.trans_method_delete, name='trans_method_delete'),

    url(r'^get-info-transaction/$', views.get_info_transaction, name='get_info_transaction'),
    url(r'^get-gl-info-transaction/$', views.get_gl_info_transaction, name='get_gl_info_transaction'),
    
    url(r'^list/pagination$', views.TransMethod__asJson, name='TransMethod__asJson'),
]