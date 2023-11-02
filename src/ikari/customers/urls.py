from django.conf.urls import url
from customers import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='customer_list'),
    url(r'^acc_customer_list/$', views.acc_customer_list, name='acc_customer_list'),
    url(r'^add/$', views.customer_add, name='customer_add'),
    url(r'^edit/(?P<customer_id>\d+)/$', views.customer_edit, name='customer_edit'),
    url(r'^get_by_pk/(?P<customer_id>.*)/(?P<rate_date>.*)/$', views.customer_By_pk, name='customer_By_pk'),
    url(r'^get_by_code/(?P<customer_code>.*)/$', views.customer_By_code, name='customer_By_code'),
    url(r'^acc_customer_add/$', views.acc_customer_add, name='acc_customer_add'),
    url(r'^acc_customer_edit/(?P<customer_id>\d+)/$', views.acc_customer_edit, name='acc_customer_edit'),
    url(r'^delete/(?P<customer_id>\d+)/$', views.customer_delete, name='customer_delete'),

    url(r'^delivery_add/$', views.delivery_add, name='delivery_add'),
    url(r'^delivery_edit/(?P<delivery_id>\d+)/$', views.delivery_edit, name='delivery_edit'),
    url(r'^delivery_edit/(?P<delivery_id>\d+)/(?P<active_tab_index>\d+)/pagination$', views.DeliveryContact__asJson,
        name='DeliveryContact__asJson'),
    url(r'^delivery_delete/(?P<delivery_id>\d+)/$', views.delivery_delete, name='delivery_delete'),
    url(r'^delivery_list/$', views.delivery_list, name='delivery_list'),
    url(r'^delivery_list/pagination$', views.DeliveryList__asJson, name='DeliveryList__asJson'),

    url(r'^item_add/(?P<customer_id>\d+)/$', views.item_add, name='customer_add_item'),
    url(r'^item_edit/(?P<custitem_id>\d+)/$', views.item_edit, name='customer_edit_item'),
    url(r'^item_delete/(?P<custitem_id>\d+)/$', views.item_delete, name='customer_delete_item'),
    url(r'^list/pagination$', views.CustomerList__asJson, name='CustomerList__asJson'),
    url(r'^item_add/(?P<customer_id>.*)/pagination$', views.CustomerItemList__asJson, name='CustomerItemList__asJson'),

    url(r'^edit/(?P<custitem_id>.*)/pagination$', views.CustomerEditItemList__asJson,
        name='CustomerEditItemList__asJson'),
    url(r'^item_add/getiteminfo$', views.get_item_info, name='get_item_info'),

    url(r'^get_customer_code_list/$', views.get_customer_code_list, name='get_customer_code_list'),
    url(r'^load_account_set/$', views.load_account_set, name='load_account_set'),
    url(r'^load_payment_code/$', views.load_payment_code, name='load_payment_code'),
    url(r'^load_tax_code/$', views.load_tax_code, name='load_tax_code'),
    url(r'^load_currency_code/$', views.load_currency_code, name='load_currency_code'),
    url(r'^account_list/$', views.AccountList__asJson, name='Customer__AccountList__asJson'),
    url(r'^account_set_list/$', views.AR_AccountSetList__asJson, name='Customer__AccountSetList__asJson'),
    url(r'^acc_customer_list/pagination$', views.AccCustomerList__asJson, name='Customer_AccCustomerList__asJson'),
    url(r'^currency_set_list/$', views.CurrencySetList__asJson, name='Customer__CurrencySetList__asJson'),
    url(r'^payment_code_set_list/$', views.PaymentModeSetList__asJson, name='Customer__PaymentModeSetList__asJson'),
    url(r'^tax_set_list/$', views.TaxSetList__asJson, name='Customer__TaxSetList__asJson'),
    url(r'^location_set_list/$', views.LocationSetList__asJson, name='Customer__LocationSetList__asJson'),
]
