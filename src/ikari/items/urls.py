from django.conf.urls import url
from items import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    # url(r'^list/$', views.load_list, name='item_list'),
    url(r'^list/$', views.load_list, name='item_list'),
    url(r'^category/pagination/(?P<menu_type>\d+)/$', views.CategoryList__asJson, name='CategoryList__asJson'),
    url(r'^category/$', views.load_category_list, name='category_list'),
    url(r'^inv_category/$', views.load_inv_category_list, name='inv_category_list'),
    url(r'^category/add/(?P<menu_type>.*)/$', views.category_add, name='category_add'),
    url(r'^category/edit/(?P<category_id>\d+)/(?P<menu_type>.*)/$', views.category_edit, name='category_edit'),
    url(r'^category/delete/(?P<category_id>\d+)/$', views.category_delete, name='category_delete'),

    url(r'^add/$', views.item_add, name='item_add'),
    url(r'^edit/(?P<item_id>\d+)/(?P<active_tab_index>\d+)/$', views.item_edit, name='item_edit'),
    url(r'^delete/(?P<item_id>.*)/$', views.item_delete, name='item_delete'),
    url(r'^get_supplier_code_by_name/(?P<supplier_name>.*)/$', views.get_supplier_code_by_name,
        name='get_supplier_code_by_name'),

    url(r'^measure/$', views.load_measure_list, name='measure_list'),
    url(r'^measure/add/$', views.measure_add, name='measure_add'),
    url(r'^measure/edit/(?P<measure_id>\d+)/$', views.measure_edit, name='measure_edit'),
    url(r'^measure/delete/(?P<measure_id>\d+)/$', views.measure_delete, name='measure_delete'),

    url(r'^customeritem_add/(?P<item_id>.*)/$', views.customeritem_add, name='customeritem_add'),
    url(r'^customeritem_edit/(?P<customeritem_id>.*)/$', views.customeritem_edit,
        name='customeritem_edit'),
    url(r'^customeritem_delete/(?P<customeritem_id>.*)/$', views.customeritem_delete, name='customeritem_delete'),

    url(r'^supplieritem_add/(?P<item_id>.*)/$', views.supplieritem_add, name='supplieritem_add'),
    url(r'^supplieritem_edit/(?P<supplieritem_id>.*)/$', views.supplieritem_edit,
        name='supplieritem_edit'),
    url(r'^supplieritem_delete/(?P<supplieritem_id>.*)/$', views.supplieritem_delete, name='supplieritem_delete'),

    url(r'^item_search/$', views.load_list_condition, name='item_list_condition'),
    url(r'^list/pagination$', views.ItemList__asJson, name='ItemList__asJson'),
    url(r'^list/loc_find_item$', views.ItemList_by_location__asJson, name='ItemList_by_location__asJson'),
    url(r'^measure/pagination$', views.MeasureList__asJson, name='MeasureList__asJson'),
    url(r'^get_item_info/$', views.get_item_info, name='items_get_item_info'),

    url(r'^get_customer_info/$', views.get_customer_info, name='get_customer_info'),
    url(r'^get_supplier_info/$', views.get_supplier_info, name='get_supplier_info'),
    url(r'^get_customer_info1/$', views.get_customer_info1, name='get_customer_info1'),
    url(r'^get_supplier_info1/$', views.get_supplier_info1, name='get_supplier_info1'),

    url(r'^customerlist/pagination$', views.CustomerList__asJson, name='ItemCustomerList__asJson'),
    url(r'^supplierlist/pagination$', views.SupplierList__asJson, name='ItemSupplierList__asJson'),

    url(r'^purchase-item/list/$', views.purchase_item_list, name='purchase_item_list'),
    url(r'^purchase-item/list/asJson/$', views.load_list_purchase_item_as_json, name='load_list_purchase_item_as_json'),
    url(r'^purchase-item/add/$', views.purchase_item_add, name='purchase_item_add'),
    url(r'^purchase-item/edit/(?P<item_id>.*)/$', views.purchase_item_edit, name='purchase_item_edit'),
    url(r'^purchase-item/delete/(?P<item_id>.*)/$', views.purchase_item_delete, name='purchase_item_delete'),

    url(r'^edit_customer/(?P<item_id>.*)/pagination$', views.CustomerEditItemList__asJson,
        name='CustomerEditItemList__asJson'),
    url(r'^edit_supplier/(?P<item_id>.*)/pagination$', views.SupplierEditItemList__asJson,
        name='SupplierEditItemList__asJson'),
    url(r'^item_loc/(?P<item_id>.*)/pagination$', views.Loc_ItemList__asJson,
        name='Loc_ItemList__asJson'),

    url(r'^part_sale_list/$', views.part_sale_list, name='part_sale_list'),
    url(r'^part_sale_list/pagination$$', views.PartSaleItemList__asJson, name='PartSaleItemList__asJson'),
    url(r'^part_sale_add/$', views.part_sale_add, name='part_sale_add'),
    url(r'^part_sale_edit/(?P<item_id>\d+)/$', views.part_sale_edit, name='part_sale_edit'),
    url(r'^part_sale_json/(?P<item_id>.*)/$', views.part_json_item, name='part_json_item'),
    url(r'^part_sale_delete/(?P<item_id>\d+)/$', views.part_sale_delete, name='part_sale_delete'),


]
