from django.conf.urls import url
from currencies import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='currency_list'),
    url(r'^all/$', views.curr_list, name='curr_list'),
    url(r'^add/(?P<menu_type>\d+)/$', views.currency_add, name='currency_add'),
    url(r'^edit/(?P<currency_id>\d+)/(?P<menu_type>\d+)/$', views.currency_edit, name='currency_edit'),
    url(r'^delete/(?P<currency_id>\d+)/$', views.currency_delete, name='currency_delete'),
    url(r'^exchange_rate_add/(?P<menu_type>.*)/$', views.exchange_rate_add, name='exchange_rate_add'),
    url(r'^exchange_rate_edit/(?P<exchange_rate_id>.*)/(?P<menu_type>.*)/$', views.exchange_rate_edit, name='exchange_rate_edit'),
    url(r'^exchange_rate_delete/(?P<exchange_rate_id>.*)/(?P<menu_type>.*)/$', views.exchange_rate_delete, name='exchange_rate_delete'),
    url(r'^exchange_rate_list/(?P<menu_type>.*)/$', views.exchange_rate_list, name='exchange_rate_list'),
    url(r'^get_exchange_rate/(?P<exchrate_type>.*)/$', views.get_exchange_rate, name='get_exchange_rate'),
    url(r'^exchange_rate_list/pagination$', views.ExchangeRate__asJson, name='ExchangeRate__asJson'),
    url(r'^search_exchange_copy/(?P<menu_type>.*)/$', views.search_exchange_copy, name='search_exchange_copy'),
    url(r'^load_exchange_copy/(?P<overwrite>.*)/(?P<menu_type>.*)/$', views.load_exchange_copy, name='load_exchange_copy'),
    url(r'^generate_exchange_copy/(?P<overwrite>.*)/(?P<menu_type>.*)/$', views.generate_exchange_copy, name='generate_exchange_copy'),
    url(r'^send_to_sp/(?P<exchrate_id>.*)/(?P<exchrate_type>.*)/$', views.send_to_sp, name='send_to_sp'),
    url(r'^list/pagination/$', views.Currencies__asJson, name='Currencies__asJson'),
    url(r'^get_exchange_by_date/(?P<is_req>.*)/(?P<id_req>.*)/(?P<rate_date>.*)/(?P<exchrate_type>.*)/$', views.get_exchange_by_rate_date, name='get_exchange_by_rate_date'),
    url(r'^tax_reporting_exch_rate/(?P<from_currency>.*)/(?P<doc_date>.*)/$', views.tax_reporting_exch_rate, name='tax_reporting_exch_rate'),

]

