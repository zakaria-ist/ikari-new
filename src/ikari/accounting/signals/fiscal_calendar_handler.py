import calendar
import datetime

from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver

from accounting.models import FiscalCalendar


# Auto generate FiscalCalendar from 2011 to CurrentYear + 1 if FiscalCalendar does not exist
@receiver(user_logged_in)
def create_fiscal_calendar(sender, request, user, **kwargs):
    start_year = datetime.datetime.today().year

    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    this_year = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0).values_list('fiscal_year', flat=True).order_by('fiscal_year').distinct()
    
    if this_year:
        this_year = int(this_year.last())
    else:
        this_year = datetime.datetime.today().year

    if (this_year - start_year) < 2:
        # fiscal_calendar = FiscalCalendar.objects.filter(fiscal_year__gte=start_year, fiscal_year__lte=(this_year + 1),
        #                                                 company_id=company_id, is_hidden=False)

        # total_records = (this_year - start_year + 2) * 12
        # fiscal_count = fiscal_calendar.count()
        # if fiscal_calendar.count() < total_records:
        while start_year <= this_year + 2:
            for i in range(1, 13):
                try:
                    fiscal_period = FiscalCalendar.objects.get(fiscal_year=start_year, period=i, company_id=company_id,
                                                            is_hidden=False)
                except ObjectDoesNotExist:
                    try:
                        fiscal_data = FiscalCalendar.objects.filter(fiscal_year=(start_year - 1), period=i, company_id=company_id,
                                                            is_hidden=False)
                        if fiscal_data:
                            fiscal_data = fiscal_data.last()
                            s_year = int(fiscal_data.start_date.year) + 1
                            e_year = int(fiscal_data.end_date.year) + 1
                            if fiscal_data.start_date.month == 2 and fiscal_data.start_date.day in [28, 29] :
                                _, num_days = calendar.monthrange(s_year, 2)
                                first_day = fiscal_data.start_date.replace(year=s_year, day=num_days)
                            else:
                                first_day = fiscal_data.start_date.replace(year=s_year)

                            if fiscal_data.end_date.month == 2 and fiscal_data.end_date.day in [28, 29]:
                                _, num_days = calendar.monthrange(e_year, 2)
                                last_day = fiscal_data.end_date.replace(year=e_year, day=num_days)
                            else:
                                last_day = fiscal_data.end_date.replace(year=e_year)
                        else:
                            _, num_days = calendar.monthrange(start_year, i)
                            first_day = datetime.date(start_year, i, 1)
                            last_day = datetime.date(start_year, i, num_days)
                    except:
                        _, num_days = calendar.monthrange(start_year, i)
                        first_day = datetime.date(start_year, i, 1)
                        last_day = datetime.date(start_year, i, num_days)

                    fiscal_period = FiscalCalendar()
                    fiscal_period.fiscal_year = start_year
                    fiscal_period.period = i
                    fiscal_period.start_date = first_day
                    fiscal_period.end_date = last_day
                    fiscal_period.company_id = company_id
                    fiscal_period.save()

                except Exception as e:
                    print(e)

            start_year += 1
