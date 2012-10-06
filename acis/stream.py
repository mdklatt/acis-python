""" Classes for streaming ACIS CSV data.

A stream class is an all-in-one for constructing a CSV data request and then
accessing the result. CSV calls are very restricted compared to JSON calls, but
the output can be streamed one record at a time rather than as a single JSON
object; this can be useful for large data requests. Metadata is stored as dict
keyed to a site identifer. Data records are streamed using the iterator
interface. The elems attribute is a tuple of element aliases for this stream.

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from .__version__ import __version__

import contextlib
import itertools

from ._misc import annotate
from ._misc import date_params
from ._misc import make_element
from ._misc import valid_interval
from .call import WebServicesCall
from .error import RequestError

__all__ = ("StnDataStream", "MultiStnDataStream")


class _CsvStream(object):
    """ Abstract base class for all CSV output.

    CSV output can be streamed, which might be useful for large requests.
    Derived classes must define the _call attribute with the appropriate
    WebServicesCall.

    """
    _call = None  # derived class must define a WebServicesCall

    def __init__(self):
        """ Initialize a _CsvStream object.

        """
        self.meta = {}
        self._params = {"output": "csv", "elems": []}
        self._interval = "dly"
        return

    @property
    def elems(self):
        """ Getter method for the elems attribute.

        This is a list of element aliases. The alias is normally just the 
        element name or "vxN" for var major N, but if there are multiple 
        instances of the same element the alias is the name plus an index 
        number, e.g. maxt_0, maxt_1, etc. 

        """
        return annotate([elem["alias"] for elem in self._params["elems"]])

    def interval(self, value):
        """ Set the interval for this stream.

        The default interval is daily ("dly").
        
        """
        self._interval = valid_interval(value)
        return

    def add_element(self, ident, **options):
        """ Add an element to this stream.

        """
        elem = make_element(ident)
        elem.update(options)
        self._params["elems"].append(elem)
        return

    def clear_elements(self):
        """ Clear all elements from this stream.

        """
        self._params["elems"] = []
        return
        
    def __iter__(self):
        """ Stream records from the server.

        """
        first_line, stream = self._connect()
        with contextlib.closing(stream):
            line_iter = itertools.chain([first_line], stream)
            self._header(line_iter)
            for line in line_iter:
                yield self._record(line.rstrip())
        return

    def _connect(self):
        """ Connect to the ACIS server.

        Execute the web services call, check for success, and return the first
        line and the stream object.

        """
        for elem in self._params['elems']:
            elem['interval'] = self._interval
        stream = self._call(self._params)
        first_line = stream.readline().rstrip()
        if first_line.startswith("error"):  # "error: error message"
            raise RequestError(first_line.split(":")[1].lstrip())
        return first_line, stream

    def _header(self, line_iter):
        """ Read the stream header.

        Derived classes should override this if the stream contains any header
        information. The iterator must be advanced to the first line of data.

        """
        return  # no header

    def _record(self, line):
        """ Process a line of data from the server.

        Each derived class must implement this to return a record of the form
        (sid, date, elem1, ...).

        """
        raise NotImplementedError


class StnDataStream(_CsvStream):
    """ A StnData stream.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location options for this request.

        StnData only accepts a single "uid" or "sid" parameter.

        """
        for key in ("uid", "sid"):  # uid takes precedence
            try:
                self._sid = self._params[key] = options[key]
            except KeyError:
                continue
            break
        else:
            raise RequestError("StnDataStream requires uid or sid")
        return

    def dates(self, sdate, edate=None):
        """ Set the date range (inclusive) for this request.

        If no edate is specified sdate is treated as a single date. The
        parameters must be a date string or "por" which means to extend to the
        period of record in that direction. Using "por" as a single date will
        return the entire period of record. The acceptable date string formats
        are YYYY-[MM-[DD]] (hyphens are optional but leading zeroes are not; no
        two-digit years).

        """
        self._params.update(date_params(sdate, edate))
        return

    def _header(self, line_iter):
        """ Read the stream header.

        """
        # The first line is the site name.
        self.meta[self._sid] = {"name": line_iter.next()}
        return

    def _record(self, line):
        """ Process a line of data from the server.

        """
        return [self._sid] + line.split(",")


class MultiStnDataStream(_CsvStream):
    """ A MultiStnData stream.

    """
    _call = WebServicesCall("MultiStnData")

    def date(self, date):
        """ Set the date for this request.

        MultStnData only accepts a single date for CSV output. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional but leading zeroes
        are not; no two-digit years).

        """
        self._params.update(date_params(date))
        return

    def location(self, **options):
        """ Set the location options for this request.

        """
        # TODO: Need to validate options.
        self._params.update(options)
        return

    def _record(self, line):
        """ Process a line of data from the server.

        The meta attribute will not be fully populated until every line has
        been receieved.

        """
        # The metadata for each site--name, state, lat/lon, and elevation--is
        # part of its data record.
        record = line.split(",")
        try:
            sid, name, state, lon, lat, elev = record[:6]
        except ValueError:  # blank line at end of output?
            raise StopIteration
        self.meta[sid] = {"name": name, "state": state}
        try:
            self.meta[sid]["elev"] = float(elev)
        except ValueError:  # elev is blank
            pass
        try:
            self.meta[sid]["ll"] = [float(lon), float(lat)]
        except ValueError:  # lat/lon is blank
            pass
        return [sid, self._params["date"]] + record[6:]
