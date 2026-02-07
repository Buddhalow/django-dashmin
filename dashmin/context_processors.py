from datetime import date

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def dashmin(request):
    period = request.GET.get('period')
    end = request.GET.get('end')
    if end:
        end = parse(end).date()
    else:
        end = date.today()

    start = request.GET.get('start')
    if start:
        start = parse(start).date()
    else:
        start = date(end.year, end.month, 1)

    if period == 'this-month':
        print(period)
        start = date(date.today().year, date.today().month, 1)

        end = start + relativedelta(months=1) - relativedelta(days=1)

    elif period == 'last-month':
        start = date(date.today().year, date.today().month, 1) - relativedelta(month=1)
        end = date(date.today().year, date.today().month, 1) - relativedelta(day=1)
    elif period == 'this-year':
        start = date(date.today().year, 1, 1)
        end = date(date.today().year, 12, 31)
    elif period == 'last-year':
        start = date(date.today().year, 1, 1) - relativedelta(year=1)
        end = date(date.today().year, 12, 31) - relativedelta(year=1)

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    q = request.GET.get('q')

    return {
      'period': period,
      'start_str': start_str,
      'end_str': end_str,
      'q': q, 
      'start': start,
      'end': end
    }
