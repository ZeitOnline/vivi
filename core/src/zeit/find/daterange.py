from datetime import datetime, timedelta
from zeit.solr import query as lq

def today_range():
    start = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end

def yesterday_range():
    start = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    end = start + timedelta(days=1)
    return start, end

def seven_day_range():
    end = datetime.now()
    start = end - timedelta(days=7)
    return start, end

def month_range():
    end = datetime.now()
    # XXX last month period if 31 days?
    start = end - timedelta(days=31)
    return start, end

def half_year_range():
    end = datetime.now()
    # last half year, about 183 days
    start = end - timedelta(days=183)
    return start, end

def year_range():
    end = datetime.now()
    # last year, about 366 days (to be on the safe side)
    start = end - timedelta(days=366)
    return start, end

DATE_RANGES = [('heute', today_range),
               ("gestern", yesterday_range),
               ("7 Tage",  seven_day_range),
               ("letzter Monat", month_range),
               ("letztes halbes Jahr", half_year_range),
               ("letztes Jahr", year_range)]

def DATE_FILTERS():
    return [(name, lq.datetime_range('last-semantic-change', *r()))
            for (name, r) in DATE_RANGES]
