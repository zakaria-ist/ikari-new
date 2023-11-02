from django.conf.urls import url
from banks import views

urlpatterns = [
    url(r'^$', views.load_list, name='index'),
    url(r'^list/$', views.load_list, name='bank_list'),
    url(r'^add/$', views.bank_add, name='bank_add'),
    url(r'^edit/(?P<bank_id>\d+)/$', views.bank_edit, name='bank_edit'),
    url(r'^delete/(?P<bank_id>.*)/$', views.bank_delete, name='bank_delete'),
    url(r'^list/paging$', views.Bank__asJson, name='Bank__asJson'),
    url(r'^account_list/$', views.AccountList__asJson, name='Bank__AccountList__asJson'),
    url(r'^load_account/$', views.load_account, name='load_account'),
]
