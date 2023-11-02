from django.conf.urls import url
from locations import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='location_list'),
    url(r'^stock/(?P<loc_id>.*)$', views.load_stock_list, name='load_stock_list'),
    url(r'^add/$', views.location_add, name='location_add'),
    url(r'^edit_loc_item/(?P<location_id>.*)/(?P<item_id>.*)/(?P<next>.*)/$', views.location_item_edit, name='location_item_edit'),
    url(r'^add_loc_item/(?P<item_id>.*)/$', views.add_loc_item, name='add_loc_item'),
    url(r'^delete_loc_item/(?P<location_id>.*)/(?P<item_id>.*)/(?P<next>.*)/$', views.delete_loc_item, name='delete_loc_item'),
    url(r'^edit/(?P<location_id>\d+)/(?P<active_tab_index>\d+)/$', views.location_edit, name='location_edit'),
    url(r'^delete/(?P<location_id>\d+)/$', views.location_delete, name='location_delete'),
    url(r'^location_item_condition/(?P<location_id>\d+)/(?P<active_tab_index>\d+)/$', views.location_item_condition,
        name='location_item_condition'),
    url(r'^location_item_search/$', views.ItemSearch_asJson, name='ItemSearch_asJson'),
    url(r'^location_item/add/$', views.location_item_add, name='location_item_add'),
    url(r'^location_category/add/$', views.location_category_add, name='location_category_add'),
    url(r'^location_item/delete/$', views.location_item_delete, name='location_item_delete'),
    url(r'^location_item/pagination$', views.LocationItemList__asJson, name='LocationItemList__asJson'),
    url(r'^list/pagination$', views.LocationList__asJson, name='LocationList__asJson'),
]
