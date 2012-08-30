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
    def __init__(self, response):
        """ Initialize a StnMetaResult object.

        The 'response' parameter is the return value from Request.submit() and
        must contain the 'uid' metadata element.

        """
        meta = response["result"]["meta"]
        try:
            self.meta = {site.pop("uid"): site for site in meta}
        except KeyError:
            raise ValueError("uid is a required meta element")
        return


class _DataResult(_Result):
    """ Base class for a station data result.

    _DataResult objects have a 'data' and 'meta' attribute corresponding to
    the data and metadata in the ACIS result object. Each attribute is a dict
    keyed to ACIS site uid(s) so the ACIS result must contain the 'uid'
    metadata element.

    """
    def __init__(self, response):
        """ Initialize a _DataResult object.

        """
        # Set up a namedtuple types for the data and smry records in this
        # result. The type names will be the same for each instance, but the
        # types are distinct.
        elements = response['params']['elems']
        try:
            # Get each name from a list of {"name": "elem"} elements.
            fields = [elem["name"] for elem in elements]
        except TypeError:  # not a dict
            # Should be a comma-delimited string instead.
            fields = [s.strip() for s in elements.split(",")]
        self._data_type = collections.namedtuple("_DataResultDataRecord",
            ["uid", "date"] + fields)
        self._smry_type = collections.namedtuple("_DataResultSmryRecord",
            fields)
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
    def __init__(self, response):
        """ Initialize a StnDataResult object.

        The 'response' parameter is the return value from Request.submit() and
        must contain the 'uid' metadata element.

        """
        _DataResult.__init__(self, response)
        meta = response["result"]["meta"]
        try:
            uid = meta.pop("uid")
        except KeyError:
            raise ValueError("uid is a required meta element")
        self.meta = {uid: meta}
        self.data = {uid: response["result"]["data"]}
        try:
            smry = response["result"]["smry"]
            self.smry = {uid: self._smry_type._make(smry)}
        except KeyError:  # no "smry"
            self.smry = {}
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).

        """
        for uid, data in self.data.items():
            for record in data:
                record[0] = _parse_date(record[0])
                record.insert(0, uid)
                yield self._data_type._make(record)
        return


class MultiStnDataResult(_DataResult):
    """ A MultiStnData result for one more sites.

    """
    def __init__(self, response):
        """ Initialize a MultiStnDataResult object.

        The 'response' parameter is the return value from Request.submit() and
        must contain the 'uid' metadata element.

        """
        _DataResult.__init__(self, response)
        try:
            sdate = response["params"]["sdate"]
        except KeyError:
            sdate = response["params"]["date"]
        try:
            interval = response["params"]["elems"][0]["interval"]
        except (TypeError, KeyError):
            interval = "dly"
        self._date_iter = _DateIterator(_parse_date(sdate), interval)
        self.meta = {}
        self.data = {}
        self.smry = {}
        for site in response["result"]["data"]:
            try:
                uid = site["meta"].pop("uid")
            except KeyError:
                raise ValueError("uid is a required meta element")
            self.meta[uid] = site["meta"]
            self.data[uid] = site["data"]
            try:
                self.smry[uid] = self._smry_type._make(site["smry"])
            except KeyError:  # no "smry"
                pass
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).  This currently does
        not work for elements with a 'groupby' specification.

        """
        for uid, data in self.data.items():
            self._date_iter.reset()
            for record in data:
                record.insert(0, uid)
                record.insert(1, self._date_iter.next())
                yield self._data_type._make(record)
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
        return next  # there is no StopIteration like a normal iterator
