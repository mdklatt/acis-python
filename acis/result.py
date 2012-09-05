""" Classes for working with an ACIS web services result object.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

Requires the dateutil library: <http//:pypi.python.org/pypi/python-dateutil/>.

"""
__version__ = "0.1.dev"

import collections
import datetime
import re

import dateutil.relativedelta as relativedelta

from . error import *


__all__ = ("StnMetaResult", "StnDataResult", "MultiStnDataResult")


def _parse_date(date):
    """ Parse a date string into a datetime.date object.

    Valid date formats are YYYY[-MM[-DD]] and hyphens are optional.
    """
    date_regex = re.compile(r"^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$")
    match = date_regex.search(date)
    try:
        y, m, d = (int(s) if s is not None else 1 for s in match.groups())
    except AttributeError:  # match is None
        raise ValueError("invalid date format")
    return datetime.date(y, m, d)


class _Result(object):
    """ Base class for all result objects.

    """
    pass


class StnMetaResult(_Result):
    """ A StnMeta result for one or more sites.

    The 'meta' attribute is a dict keyed to ACIS site uid(s).

    """
    def __init__(self, params, result):
        """ Initialize a StnMetaResult object.

        The 'result' parameter is the result object returned from the ACIS
        server and must contain the 'uid' metadata element. The 'params'
        parameter is ignored.

        """
        try:
            self.meta = {site.pop("uid"): site for site in result["meta"]}
        except KeyError:
            raise ParameterError("uid is a required meta element")
        return


class _DataResult(_Result):
    """ Base class for a station data result.

    _DataResult objects have a 'data' and 'meta' attribute corresponding to
    the data and metadata in the ACIS result object. Each attribute is a dict
    keyed to ACIS site uid(s) so the ACIS result must contain the 'uid'
    metadata element.

    """
    def __init__(self, params):
        """ Initialize a _DataResult object.

        """
        elems = params["elems"]
        try:
            # a comma-delimited string
            self.fields = [elem.strip() for elem in elems.split(",")]
        except AttributeError:  # no split(), not a string
            try:
                # a sequence of dicts
                self.fields = [elem["name"] for elem in params["elems"]]
            except TypeError:  # no string indices, not a dict
                # a sequence of strings
                self.fields = elems
        return

    def __len__(self):
        """ Return the number of data records in this result.

        """
        count = 0
        for uid in self.data:
            count += len(self.data[uid])
        return count


class StnDataResult(_DataResult):
    """ A StnData result for a single site.

    """
    def __init__(self, params, result):
        """ Initialize a StnDataResult object.

        The 'result' parameter is the result object returned from the ACIS
        server and must contain the 'uid' metadata element.

        """
        super(StnDataResult, self).__init__(params)
        try:
            uid = result["meta"].pop("uid")
        except KeyError:
            raise ParameterError("uid is a required meta element")
        self.meta = {uid: result["meta"]}
        self.data = {uid: result["data"]}
        smry = result.get("smry", [])
        self.smry = {uid: collections.OrderedDict(zip(self.fields, smry))}
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).

        """
        fields = ["uid", "date"] + self.fields
        for uid, data in self.data.items():
            for record in data:
                record.insert(0, uid)
                yield collections.OrderedDict(zip(fields, record))
        return


class MultiStnDataResult(_DataResult):
    """ A MultiStnData result for one more sites.

    """
    def __init__(self, params, result):
        """ Initialize a MultiStnDataResult object.

        The 'result' parameter is the return value from Request.submit() and
        must contain the 'uid' metadata element.

        """
        super(MultiStnDataResult, self).__init__(params)
        try:
            sdate = params["sdate"]
        except KeyError:
            sdate = params["date"]
        try:
            interval = params["elems"][0]["interval"]
        except (TypeError, KeyError):
            interval = "dly"
        self._date_iter = _DateIterator(_parse_date(sdate), interval)
        self.meta = {}
        self.data = {}
        self.smry = {}
        for site in result["data"]:
            try:
                uid = site["meta"].pop("uid")
            except KeyError:
                raise ParameterError("uid is a required meta element")
            self.meta[uid] = site["meta"]
            self.data[uid] = site["data"]
            try:
                smry = site["smry"]
            except KeyError:  # no "smry"
                continue
            self.smry[uid] = collections.OrderedDict(zip(self.fields, smry))
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).  This currently does
        not work for elements with a 'groupby' specification.

        """
        fields = ["uid", "date"] + self.fields
        for uid, data in self.data.items():
            self._date_iter.reset()
            for record in data:
                record.insert(0, uid)
                record.insert(1, self._date_iter.next())
                yield collections.OrderedDict(zip(fields, record))
        return


class _DateIterator(object):
    """ An endless date iterator.

    Iteration will continue indefinitely from the start date unless reset() is
    called.

    """
    _deltas = {
        "dly": datetime.timedelta(days=1),
        "mly": relativedelta.relativedelta(months=1),
        "yly": relativedelta.relativedelta(years=1),
    }

    def __init__(self, start, interval):
        """ Initialize a _DateIterator object.

        The 'interval' is valid ACIS interval specifier, e.g. 'dly', 'mly',
        or 'yly'.
        """
        self._start = self._now = start
        try:
            self._delta = _DateIterator._deltas[interval]
        except KeyError:
            raise ValueError("uknown interval %s" % interval)
        return

    def reset(self):
        """ Reset the iterator to its start date. """
        self._now = self._start

    def next(self):
        """ Return the next date in the sequence. """
        next = self._now
        self._now += self._delta
        return next.strftime("%Y-%m-%d");  # no StopIteration
