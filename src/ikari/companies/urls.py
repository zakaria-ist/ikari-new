from django.conf.urls import url
from companies import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='company_list'),
    url(r'^list/paging$', views.CompanyList__asJson, name='CompanyList__asJson'),
    url(r'^add/$', views.company_add, name='company_add'),
    url(r'^edit/(?P<company_id>.*)/(?P<is_profile>.*)/(?P<menu_type>.*)/$', views.company_edit, name='company_edit'),
    url(r'^delete/(?P<company_id>\d+)/$', views.company_delete, name='company_delete'),
    url(r'^profile/$', views.company_profile, name='company_profile'),
    url(r'^control/$', views.control_file, name='control_file'),
    url(r'^cost_centers_list/$', views.cost_centers_list, name='cost_centers_list'),
    url(r'^cost_centers/$', views.cost_centers, name='cost_centers'),
    url(r'^cost_centers_add/(?P<menu_type>.*)/$', views.cost_centers_add, name='cost_centers_add'),
    url(r'^cost_centers_edit/(?P<cost_id>.*)/(?P<menu_type>.*)/$', views.cost_centers_edit, name='cost_centers_edit'),
    url(r'^cost_centers_delete/(?P<cost_id>.*)/$', views.cost_centers_delete, name='cost_centers_delete'),
    url(r'^cost_centers_list/pagination$', views.CostCenter__asJson, name='CostCenter__asJson'),
    url(r'^list_segment/$', views.segment_list, name='segment_list'),
    url(r'^add_segment/$', views.segment_add, name='segment_add'),
    url(r'^edit_segment/(?P<segment_id>.*)/$', views.segment_edit, name='segment_edit'),
    url(r'^delete_segment/(?P<segment_id>.*)/$', views.segment_delete, name='segment_delete'),
]
