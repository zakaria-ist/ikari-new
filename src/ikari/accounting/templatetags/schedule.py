from django import template

register = template.Library()


@register.filter
def return_period(period):
    try:
        if 0 == period:
            return 'Daily'
        if 1 == period:
            return 'Weekly'
        if 2 == period:
            return 'Semi-Monthly'
        if 3 == period:
            return 'Monthly'
        if 4 == period:
            return 'Yearly'
    except:
        return period
    return ''

@register.filter
def return_frequency(schedule):
    try:
        if 0 == schedule.recur_period:
            return schedule.daily_frequency
        if 1 == schedule.recur_period:
            return schedule.weekly_frequency
        if 2 == schedule.recur_period:
            return schedule.monthly_frequency
        if 3 == schedule.recur_period:
            return schedule.monthly_frequency
        if 4 == schedule.recur_period:
            return get_month_names(schedule.frequency_month)
    except:
        return ''
    return ''

@register.filter
def return_day(schedule):
    try:
        if 0 == schedule.recur_period:
            return ''
        if 1 == schedule.recur_period:
            return get_week_days(schedule.frequency_weekday_index)
        if 2 == schedule.recur_period:
            return get_days(schedule.frequency_date)
        if 3 == schedule.recur_period:
            return get_days(schedule.frequency_date)
        if 4 == schedule.recur_period:
            return get_days(schedule.frequency_date)
    except:
        return ''
    return ''


def get_week_days(frequency):
    try:
        if 0 == frequency:
            return 'Monday'
        if 1 == frequency:
            return 'Tuesday'
        if 2 == frequency:
            return 'Wednesday'
        if 3 == frequency:
            return 'Thursday'
        if 4 == frequency:
            return 'Friday'
        if 5 == frequency:
            return 'Saturday'
        if 6 == frequency:
            return 'Sunday'
    except:
        return ''
    return ''


def get_month_names(frequency_month):
    try:
        if 0 == frequency_month:
            return 'January'
        if 1 == frequency_month:
            return 'February'
        if 2 == frequency_month:
            return 'March'
        if 3 == frequency_month:
            return 'April'
        if 4 == frequency_month:
            return 'May'
        if 5 == frequency_month:
            return 'June'
        if 6 == frequency_month:
            return 'July'
        if 7 == frequency_month:
            return 'August'
        if 8 == frequency_month:
            return 'September'
        if 9 == frequency_month:
            return 'October'
        if 10 == frequency_month:
            return 'November'
        if 11 == frequency_month:
            return 'December'
    except:
        return ''
    return ''


def get_days(frequency_date):
    try:
        if 0 == frequency_date:
            return '1st'
        if 1 == frequency_date:
            return '2nd'
        if 2 == frequency_date:
            return '3rd'
        if 3 == frequency_date:
            return '4th'
        if 4 == frequency_date:
            return '5th'
        if 5 == frequency_date:
            return '6th'
        if 6 == frequency_date:
            return '7th'
        if 7 == frequency_date:
            return '8th'
        if 8 == frequency_date:
            return '9th'
        if 9 == frequency_date:
            return '10th'
        if 10 == frequency_date:
            return '11th'
        if 11 == frequency_date:
            return '12th'
        if 12 == frequency_date:
            return '13th'
        if 13 == frequency_date:
            return '14th'
        if 14 == frequency_date:
            return '15th'
        if 15 == frequency_date:
            return '16th'
        if 16 == frequency_date:
            return '17th'
        if 17 == frequency_date:
            return '18th'
        if 18 == frequency_date:
            return '19th'
        if 19 == frequency_date:
            return '20th'
        if 20 == frequency_date:
            return '21st'
        if 21 == frequency_date:
            return '22th'
        if 22 == frequency_date:
            return '23th'
        if 23 == frequency_date:
            return '24th'
        if 24 == frequency_date:
            return '25th'
        if 25 == frequency_date:
            return '26th'
        if 26 == frequency_date:
            return '27th'
        if 27 == frequency_date:
            return '28th'
        if 28 == frequency_date:
            return '29th'
        if 29 == frequency_date:
            return '30th'
        if 30 == frequency_date:
            return '31st'
    except:
        return ''
    return ''
