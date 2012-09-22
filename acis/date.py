""" ACIS date-handling functions.

This module contains functions for converting ACIS date strings to/from Python
date objects (e.g. datetime.date and datetime.datetime), and a function to
calculate a date range based on ACIS call parameters.

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

The external dateutil library is required:
    <http://pypi.python.org/pypi/python-dateutil>.

"""
from .__version__ import __version__

import datetime
import re

import dateutil.relativedelta

__all__ = ("date_object", "date_string", "date_range")


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

    The date_obj parameter can be any object that has year, month, and day
    attributes, e.g. datetime.date or datetime.datetime. The datetime versions
    of strftime() cannot handle dates before 1900, so this should be used
    instead.

    """
    try:
        yr, mo, da = date_obj.year, date_obj.month, date_obj.day
    except AttributeError:
        raise TypeError("need a date object")
    return "{0:04d}-{1:02d}-{2:02d}".format(yr, mo, da)


def _delta(interval):
    """ Determine the date delta for an interval.

    An interval can be a name ("dly", "mly", "yly") or a (yr, mo, da) value
    given as a list/tuple or comma-delimited string. For (yr, mo, da) the least
    significant nonzero value sets the interval, e.g. "0, 3, 0" is an interval
    of 3 months.

    """
    named_deltas = {
        "dly": (0, 0, 1),
        "mly": (0, 1, 0),
        "yly": (1, 0, 0),
    }
    try:
        yr, mo, da = named_deltas[interval]
    except (KeyError, TypeError):  # unknown delta or not a str
        try:  # comma-delimited string?
            yr, mo, da = (int(x) for x in interval.split(","))
        except AttributeError:  # no split, not a str
            yr, mo, da = interval
    mo = 0 if da > 0 else mo
    yr = 0 if (mo > 0 or da > 0) else yr 
    return dateutil.relativedelta.relativedelta(years=yr, months=mo, days=da)


def date_range(params):
    """ Return a generator expression for the date range specified by params.

    The params parameter is a dict of options defining an ACIS call. The
    returned date range will be the dates for a result returned by that
    call. This cannot be used for period-of-record ("por") date ranges.

    IN THE CURRENT IMPLEMENTATION THE RESULTS FOR A "GROUPBY" RESULT WILL NOT
    BE CORRECT.

    """
    try:
        sdate = date_object(params["sdate"])
        edate = date_object(params["edate"])
    except KeyError:
        try:  # single date?
            yield params["date"]
        except KeyError:
            raise ValueError("invalid date range specification")
        return
    try:
        # All elements must have the same interval, so check the first element
        # for an interval specification.
        interval = params["elems"][0]["interval"]
    except (TypeError, KeyError):
        interval = (0, 0, 1)  # default value is daily
    delta = _delta(interval)
    while sdate <= edate:
        yield date_string(sdate)
        sdate += delta
    return
