import calendar
import datetime

from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.dispatch import receiver

from accounts.models import AccountHistory, Account
from companies.models import Company


# Auto generate FiscalCalendar from currenct_year-1 to CurrentYear + 1 if FiscalCalendar does not exist
@receiver(user_logged_in)
def create_history_calendar(sender, request, user, **kwargs):
    this_year = datetime.datetime.today().year
    start_year = this_year - 1

    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    accounts = Account.objects.filter(
        Q(company_id=company_id), is_active=True, is_hidden=False).order_by('account_segment')

    total_records = (this_year - start_year + 2) * 14

    for account in accounts:
        start_year = this_year - 1
        account_history_list = AccountHistory.objects.filter(period_year__gte=start_year,
                                                             period_year__lte=(this_year + 1), company_id=company_id,
                                                             account_id=account.id, is_hidden=False)

        last_day = None
        if account_history_list.count() < total_records:
            while start_year < this_year + 2:
                for i in range(1, 13):
                    try:
                        account_history = AccountHistory.objects.get(period_year=start_year, period_month=i,
                                                                     account_id=account.id, company_id=company_id,
                                                                     is_hidden=False, source_currency_id=company.currency_id,
                                                                     functional_currency_id=company.currency_id)
                    except ObjectDoesNotExist:
                        _, num_days = calendar.monthrange(start_year, i)
                        last_day = datetime.date(start_year, i, num_days)

                        account_history = AccountHistory()
                        account_history.period_year = start_year
                        account_history.period_month = i
                        account_history.period_date = last_day
                        account_history.company_id = company_id
                        account_history.account_id = account.id
                        account_history.source_currency_id = company.currency_id
                        account_history.functional_currency_id = company.currency_id
                        account_history.save()
                    except MultipleObjectsReturned:
                        pass

                if not last_day:
                    last_day = str(start_year) + '-12-31'

                try:
                    account_history = AccountHistory.objects.get(period_year=start_year, period_month='ADJ',
                                                                account_id=account.id, company_id=company_id,
                                                                is_hidden=False, source_currency_id=company.currency_id,
                                                                functional_currency_id=company.currency_id)
                except ObjectDoesNotExist:
                    account_history = AccountHistory()
                    account_history.period_year = start_year
                    account_history.period_month = 'ADJ'
                    account_history.period_date = last_day
                    account_history.company_id = company_id
                    account_history.account_id = account.id
                    account_history.source_currency_id = company.currency_id
                    account_history.functional_currency_id = company.currency_id
                    account_history.save()

                try:
                    account_history = AccountHistory.objects.get(period_year=start_year, period_month='CLS',
                                                                 account_id=account.id, company_id=company_id,
                                                                 is_hidden=False, source_currency_id=company.currency_id,
                                                                 functional_currency_id=company.currency_id)
                except ObjectDoesNotExist:
                    account_history = AccountHistory()
                    account_history.period_year = start_year
                    account_history.period_month = 'CLS'
                    account_history.period_date = last_day
                    account_history.company_id = company_id
                    account_history.account_id = account.id
                    account_history.source_currency_id = company.currency_id
                    account_history.functional_currency_id = company.currency_id
                    account_history.save()

                start_year += 1
