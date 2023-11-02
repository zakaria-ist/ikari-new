from django.conf.urls import url
from taxes import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='tax_list'),
    url(r'^acc_tax_list/$', views.acc_tax_list, name='acc_tax_list'),
    url(r'^add/(?P<module_type>.*)/$', views.tax_add, name='tax_add'),
    url(r'^edit/(?P<tax_id>.*)/(?P<module_type>.*)/$', views.tax_edit, name='tax_edit'),
    # url(r'^delete/(?P<tax_id>\d+)/$', views.tax_delete, name='tax_delete'),
    url(r'^delete/(?P<tax_id>.*)/(?P<module_type>.*)/$', views.tax_delete, name='tax_delete'),
    url(r'^list/pagination$', views.TaxList__asJson, name='TaxList__asJson'),
    url(r'^tax_authority_list/$', views.tax_authority_list, name='tax_authority_list'),
    url(r'^tax_authority_list/pagination$', views.TaxAuthorityList__asJson, name='TaxAuthorityList__asJson'),
    url(r'^tax_authority_add/$', views.tax_authority_add, name='tax_authority_add'),
    url(r'^tax_authority_edit/(?P<tax_authority_id>.*)/$', views.tax_authority_edit, name='tax_authority_edit'),
    url(r'^tax_authority_delete/(?P<tax_authority_id>.*)/$', views.tax_authority_delete, name='tax_authority_delete'),
    url(r'^tax_group_list/$', views.tax_group_list, name='tax_group_list'),
    url(r'^tax_group_list/pagination$', views.TaxGroupList__asJson, name='TaxGroupList__asJson'),
    url(r'^tax_group_add/$', views.tax_group_add, name='tax_group_add'),
    url(r'^tax_group_edit/(?P<tax_group_id>.*)/$', views.tax_group_edit, name='tax_group_edit'),
    url(r'^tax_group_delete/(?P<tax_group_id>.*)/$', views.tax_group_delete, name='tax_group_delete'),
]
