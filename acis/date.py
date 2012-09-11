""" ACIS date-handling functions.

Requires the dateutil library: <http://pypi.python.org/pypi/python-dateutil>.

"""
__version__ = "0.1.dev"

import datetime
import re

import dateutil.relativedelta as relativedelta

from . error import ParameterError

_DATE_REGEX = re.compile(r"^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$")


def date_object(date_str):
    """ Convert an ACIS date string to a datetime.date object.

    Valid date formats are YYYY[-MM[-DD]] (hyphens are optional but leading
    zeroes are not; no two-digit years).

    """
    match = _DATE_REGEX.search(date_str)
    try:
        yr, mo, da = (int(s) if s is not None else 1 for s in match.groups())
    except AttributeError:  # match is None
        raise ValueError("invalid date format: {0:s}".format(date_str))
    return datetime.date(yr, mo, da)


def date_string(date_obj):
    """ Return an ACIS-format date string from a date object.

    NOTE: datetime.strftime() cannot handle dates before 1900, so this should
    be used instead.

    """
    try:
        yr, mo, da = date_obj.year, date_obj.month, date_obj.day
    except AttributeError:
        raise TypeError("need a date object")
    return "{0:04d}-{1:02d}-{2:02d}".format(yr, mo, da)


def date_range(params):
    """ Return a generator expression for the date range specified by 'params'.

    """
    try:
        sdate = date_object(params["sdate"])
        edate = date_object(params["edate"])
    except KeyError:
        try:
            yield params["date"]
        except KeyError:
            raise ParameterError("invalid date range specification")
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
        yield date_string(sdate)
        sdate += deltas[interval]
    return

