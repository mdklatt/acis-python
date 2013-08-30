""" ACIS date-handling functions.

This module contains functions for converting ACIS date strings to/from Python
date objects (e.g. datetime.date and datetime.datetime), and a function to
calculate a date range based on ACIS call parameters.

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

The external dateutil library is required:
    <http://pypi.python.org/pypi/python-dateutil>.

"""
from __future__ import absolute_import

from datetime import date
from re import compile

from dateutil.relativedelta import relativedelta

__all__ = ("date_object", "date_string", "date_trunc", "date_range")

_DATE_REGEX = compile(r"^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$")


def date_object(datestr):
    """ Convert an ACIS date string to a datetime.date object.

    Valid date formats are YYYY[-MM[-DD]] (hyphens are optional but leading
    zeroes are not; no two-digit years).

    """
    match = _DATE_REGEX.search(datestr)
    try:
        y, m, d = (int(s) if s is not None else 1 for s in match.groups())
    except AttributeError:  # match is None
        raise ValueError("invalid date format: {0:s}".format(datestr))
    return date(y, m, d)


def date_string(dateobj):
    """ Return an ACIS date string from a date object.

    The date_obj parameter can be any object that has year, month, and day
    attributes, e.g. datetime.date or datetime.datetime. The datetime versions
    of strftime() cannot handle dates before 1900, so this should be used
    instead.

    """
    try:
        y, m, d = dateobj.year, dateobj.month, dateobj.day
    except AttributeError:
        raise TypeError("need a date object")
    return "{0:04d}-{1:02d}-{2:02d}".format(y, m, d)


def date_delta(interval):
    """ Determine the date delta for an interval.

    An interval can be a name ("dly", "mly", "yly") or a (y, m, d) sequence.
    
    """
    named_deltas = {
        "dly": (0, 0, 1),
        "mly": (0, 1, 0),
        "yly": (1, 0, 0)}
    try:
        interval = named_deltas[interval.lower()]
    except AttributeError:  # not a str
        pass
    y, m, d = interval
    return relativedelta(years=y, months=m, days=d)


def date_trunc(datestr, interval):
    """ Truncate a date to the precision defined by interval.
    
    The only intervals that have an effect are "yly" and "mly". For all other
    intervals, including (y, m, d) sequences, the precision is daily.
    
    """
    try:
        y, m, d = _DATE_REGEX.search(datestr).groups()
    except AttributeError:  # match is None
        raise ValueError("invalid date string: {0:s}".format(datestr))
    precision = {"yly": 1, "mly": 2}
    try:
        prec = precision[interval.lower()]
    except (AttributeError, KeyError):  # not a str or unknown interval
        prec = 3  # daily
    datestr = [y]
    if prec >= 2:
        datestr.append(m if m is not None else "01")
    if prec == 3:
        datestr.append(d if d is not None else "01")
    return "-".join(datestr)

    
def date_range(sdate, edate=None, interval="dly"):
    """ Return a date range.

    A generator expression is created for a date range based on the start date,
    end date (inclusive), and interval. A single date is returned if edate is
    None. The interval can be "yly", "mly", "dly" or a (y, m, d) sequence.
    The returned dates will have the precision defined by interval (see the
    date_trunc function).
    
    """
    if edate is None:
        edate = sdate
    sdate = date_object(date_trunc(sdate, interval))
    edate = date_object(date_trunc(edate, interval))
    delta = date_delta(interval)
    while sdate <= edate:
        yield date_trunc(date_string(sdate), interval)
        sdate += delta
    return