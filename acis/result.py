"""
Classes for working with an ACIS result object.

"""
__version__ = '0.1.dev'
__all__ = ('StnMetaResult', 'StnDataResult', 'MultiStnDataResult',
    'ResultError')

import datetime
import re
import dateutil.relativedelta as relativedelta


def _parse_date(sdate):
    """
    Parse a date string into a datetime.date object.

    Valid date formats are YYYY[-MM[-DD]] and hyphens are optional.
    """
    date_regex = re.compile(r'^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$')
    match = date_regex.search(sdate)
    try:
        y, m, d = (int(s) if s is not None else 1 for s in match.groups())
    except AttributeError:  # match is None
        raise ValueError('invalid date format')
    return datetime.date(y, m, d)


class _Result(object):

    def __init__(self, request):
        try:
            raise ResultError(request['result']['error'])
        except KeyError:  # no error
            pass
        return


class StnMetaResult(_Result):

    def __init__(self, request):
        _Result.__init__(self, request)
        meta = request['result']['meta']
        try:
            self.meta = { site.pop('uid'): site for site in meta }
        except KeyError:
            raise ValueError('uid is a required meta element')
        return


class _DataResult(_Result):

    def __len__(self):
        count = 0
        for uid in self.data:
            count += len(self.data[uid])
        return count


class StnDataResult(_DataResult):
    """
    A StnData request result.

    """
    def __init__(self, request):
        _DataResult.__init__(self, request)
        meta = request['result']['meta']
        try:
            uid = meta.pop('uid')
        except KeyError:
            raise ValueError('uid is a required meta element')
        self.meta = { uid: meta }
        self.data = { uid: request['result']['data'] }
        return

    def __iter__(self):
        for uid, data in self.data.items():
            for record in data:
                record[0] = _parse_date(record[0])
                record.insert(0, uid)
                yield tuple(record)
        return


class MultiStnDataResult(_DataResult):

    def __init__(self, request):
        _DataResult.__init__(self, request)
        try:
            sdate = request['params']['sdate']
        except KeyError:
            sdate = request['params']['date']
        try:
            interval = request['params']['elems'][0]['interval']
        except (TypeError, KeyError):
            interval = 'dly'
        self._date_iter = _DateIterator(_parse_date(sdate), interval)
        self.meta = {}
        self.data = {}
        for site in request['result']['data']:
            try:
                uid = site['meta'].pop('uid')
            except KeyError:
                raise ValueError('uid is a required meta element')
            self.meta[uid] = site['meta']
            self.data[uid] = site['data']
        return

    def __iter__(self):
        for uid, data in self.data.items():
            self._date_iter.reset()
            for record in data:
                record.insert(0, uid)
                record.insert(1, self._date_iter.next())
                yield tuple(record)
        return


class ResultError(Exception):
    """
    The returned result object is reporting an error.

    This is reported as an 'error' attribute in the result object. The server
    was able to parse the request, but the result is invalid in some way.
    """
    pass


class _DateIterator(object):
    """
    An endless date iterator.

    Call reset() to reset the iterator to the beginning.
    """
    _deltas = {
        'dly': datetime.timedelta(days=1),
        'mly': relativedelta.relativedelta(months=1),
        'yly': relativedelta.relativedelta(years=1),
    }

    def __init__(self, start, interval):
        self._start = self._now = start
        try:
            self._delta = _DateIterator._deltas[interval]
        except KeyError:
            raise ValueError('uknown interval %s' % interval)
        return

    def reset(self):
        self._now = self._start

    def next(self):
        next = self._now
        self._now += self._delta
        return next
