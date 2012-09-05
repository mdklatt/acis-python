""" ACIS date-handling functions.

Requires the dateutil library: <http://pypi.python.org/pypi/python-dateutil>.

"""
__version__ = "0.1.dev"

import datetime
import re

import dateutil.relativedelta as relativedelta

from . error import *


_DATE_REGEX = re.compile(r"^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$")


def parse_date(date):
    """ Convert an ACIS date string to a datetime.date object.

    Valid date formats are YYYY[-MM[-DD]] (hyphens are optional).

    """
    try:
        match = _DATE_REGEX.search(date)
    except TypeError:
        raise TypeError("need a date string")
    try:
        y, m, d = (int(s) if s is not None else 1 for s in match.groups())
    except AttributeError:  # match is None
        raise ValueError("invalid date format")
    return datetime.date(y, m, d)


def format_date(date):
    """ Return an ACIS-format date string from a date object.

    NOTE: datetime.strftime() cannot handle dates before 1900, so this should
    be used instead.

    """
    try:
        y, m, d = date.year, date.month, date.day
    except AttributeError:
        raise TypeError("need a date object")
    return "%04d-%02d-%02d" % (y, m, d)


def date_range(params):
    """ Return a generator expression for the date range specified by 'params'.

    """
    try:
        sdate = parse_date(params["sdate"])
        edate = parse_date(params["edate"])
    except KeyError:
        try:
            yield params["date"]
        except KeyError:
            raise ParameterError('invalid date range specification')
        return  # single date
    try:
        interval = params["elems"][0]["interval"]
    except (TypeError, KeyError):
        interval = "dly"
    deltas = {
        "dly": datetime.timedelta(days=1),
        "mly": relativedelta.relativedelta(months=1),
        "yly": relativedelta.relativedelta(years=1),
    }
    while sdate <= edate:
        yield format_date(sdate)
        sdate += deltas[interval]
    return

