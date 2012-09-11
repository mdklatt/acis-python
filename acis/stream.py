""" Classes for streaming ACIS CSV records.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
__version__ = "0.1.dev"

import collections
import itertools

from . call import WebServicesCall 
from . date import date_string
from . date import date_object
from . error import ParameterError 
from . error import ResultError 

__all__ = ("StnDataStream", "MultiStnDataStream")


class _CsvStream(object):
    """ Private base class for all CSV output.

    CSV output is more limited than JSON output, but it can be streamed which
    might be useful for large requests. A _CsvStream is like a _JsonRequest
    that also provides some limited functionality of a _JsonResult.

    """
    _call = WebServicesCall(None)

    def __init__(self):
        self.meta = {}
        self.fields = []
        self._params = {"output": "csv", "elems": []}
        self._interval = "dly"
        return

    def _connect(self):
        """ Connect to the ACIS server.

        Executes the web services call, checks for success, and returns the
        stream.

        """
        stream = self._call(self._params)
        header = stream.readline().rstrip()
        if header.startswith("error"):  # "error: error message"
            raise ResultError(header.split(":")[1].lstrip())
        return header, stream

    def add_elem(self, name, **options):
        """ Add element "name" to this request with any "options".

        """
        if set(options) > set(("duration", "reduce")):
            raise ParameterError("invalid element options")
        elem = {"name": name, "interval": self._interval}
        elem.update(options)
        self.fields.append(name)
        self._params["elems"].append(elem)
        return

    def clear_elem(self, name=None):
        """ Clear all or just "name" from the stream elements.

        """
        if name is not None:
            self._params.pop(name)
        else:
            self._params["elems"] = []
        return


class StnDataStream(_CsvStream):
    """ A StnData stream.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location for this request.

        """
        for key in ("uid", "sid"):  # uid takes precedence
            oid = options.get(key)
            if not oid:
                continue
            oid = options[key]
            self._params[key] = oid
            self._site = (key, oid)
            break  # or else the exception is triggered below
        else:
            raise ParameterError("StnDataStream requires uid or sid")
        return

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this stream.

        If no "edate" is specified "sdate" is treated as a single date. The
        parameters must be a date string or the value "por" which means to
        extend to the period-of-record in that direction. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional; no two-digit years).

        """
        if edate is None:  # single date
            self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def __iter__(self):
        """ Stream the records returned by the server.

        """
        header, stream = self._connect()  # header is site name
        key, oid = self._site
        self.meta.setdefault(oid, {})["name"] = header
        fields = [key, "date"] + self.fields
        for line in stream:
            record = [oid] + line.rstrip().split(",")
            yield collections.OrderedDict(zip(fields, record))
        return


class MultiStnDataStream(_CsvStream):
    """ A MultiStnData stream.

    A MultiStnData CSV call is limited to a single date.

    """
    _call = WebServicesCall("MultiStnData")

    def date(self, date):
        """ Specify the date for this stream.

        MultStnData only accepts a single date for CSV output. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional).

        """
        self._params["date"] = date_string(date_object(date))  # validation
        return

    def location(self, **options):
        """ Define the location for this request.

        """
        # Need to validate options.
        self._params.update(options)
        return

    def __iter__(self):
        """ Stream the records returned by the server.

        """
        header, stream = self._connect()  # header is a regular record
        fields = ["sid", "date"] + self.fields
        self.meta = {}
        for line in itertools.chain([header], stream):
            record = line.rstrip().split(",")
            try:
                sid, name, state, lon, lat, elev = record[:6]
            except ValueError:  # blank line at end of output?
                break
            self.meta[sid] = {"name": name, "state": state,
                    "elev": float(elev), "ll": [float(x) for x in (lon, lat)]}
            record = [sid, self._params["date"]] + record[6:]
            yield collections.OrderedDict(zip(fields, record))
        return
