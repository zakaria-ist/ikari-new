from django.conf.urls import url
from staffs import views

urlpatterns = [

    url(r'^$', views.load_staff_list, name='staff_list'),
    url(r'^list/$', views.load_staff_list, name='staff_list'),
    url(r'^add/$', views.staff_add, name='staff_add'),
    url(r'^edit/(?P<staff_id>\d+)/$', views.staff_change_info, name='staff_edit'),
    url(r'^delete/(?P<staff_id>\d+)/$', views.staff_delete, name='staff_delete'),
    url(r'^profile/$', views.user_profile, name='user_profile'),
    url(r'^image/$', views.image_profile, name='image_profile'),
    url(r'^password_change/$', views.password_change, name='password_change'),
    url(r'^group/$', views.load_group_list, name='load_group_list'),
    url(r'^group/add/$', views.group_add, name='group_add'),
    url(r'^group/edit/(?P<group_id>\d+)/$', views.group_edit, name='group_edit'),
    url(r'^group/delete/(?P<group_id>\d+)/$', views.group_delete, name='group_delete'),
    url(r'^reset_password/(?P<user_name>.*)/(?P<old_password>.*)/$', views.reset_password, name='reset_password'),
    url(r'^reset_confirm/$', views.reset_confirm, name='reset_confirm'),
    url(r'^list/pagination/$', views.Staff__asJson, name='Staff__asJson'),
    url(r'^group_list/$', views.Group_list__asJson, name='Group_list__asJson'),
    url(r'^init_group/$', views.reassign_group_permission, name='reassign_group_permission'),
]
