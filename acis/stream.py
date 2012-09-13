""" Classes for streaming ACIS CSV data.

A stream class is an all-in-one for constructing a CSV data request and then
accessing the result. CSV calls are very restricted compared to JSON calls, but
the output can be streamed one record at a time rather than as a single JSON
object; this can be useful for large data requests. Metadata is stored as dict
keyed to a site identifer. Data records are streamed using the iterator
interface. The elems attribute is a tuple of element names for this stream.
See the call, request, and result modules if a CSV request is too limited.

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from .__version__ import __version__

import itertools

from .call import WebServicesCall
from .error import RequestError
from .error import ResultError

__all__ = ("StnDataStream", "MultiStnDataStream")


class _CsvStream(object):
    """ Private base class for all CSV output.

    CSV output can be streamed, which might be useful for large requests.

    """
    _call = None  # child classes must set to an appropriate WebServicesCall

    def __init__(self):
        """ Initialize a _CsvStream object.

        """
        self.meta = {}
        self._params = {"output": "csv", "elems": []}
        self._interval = "dly"
        return

    @property
    def elems(self):
        """ Getter method for the elems attribute. """
        return tuple(elem["name"] for elem in self._params["elems"])

    def add_element(self, name, **options):
        """ Add an element to this request.

        """
        new_elem = dict([("name", name)] + options.items())
        elements = self._params["elems"]
        for pos, elem in enumerate(elements):
            if elem["name"] == name:
                elements[pos] = new_elem
                break
        else:
            elements.append(new_elem)
        return

    def del_element(self, name=None):
        """ Delete all or just "name" from the requested elements.

        """
        if name is None:
            self._params["elems"] = []
        elements = self._params["elems"]
        for pos, elem in enumerate(elements):
            if elem["name"] == name:
                elements.pop(pos)
                break
        return

    def __iter__(self):
        """ Stream the records from the server.

        Each record is of the form (sid, date, elem1, ...).

        """
        raise NotImplementedError

    def _connect(self):
        """ Connect to the ACIS server.

        Executes the web services call, check for success, and return the
        result header (the first line) and the stream object. The header has
        a different meaning depending on the call type.

        """
        stream = self._call(self._params)
        header = stream.readline().rstrip()
        if header.startswith("error"):  # "error: error message"
            raise RequestError(header.split(":")[1].lstrip())
        return header, stream


class StnDataStream(_CsvStream):
    """ A StnData stream.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location for this request.

        StnData only accepts a single "uid" or "sid" parameter.

        """
        for key in ("uid", "sid"):  # uid takes precedence
            try:
                sid = self._params[key] = options[key]
            except KeyError:
                continue
            self.meta[sid] = {}
            break
        else:
            raise RequestError("StnDataStream requires uid or sid")
        return

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        If no "edate" is specified "sdate" is treated as a single date. The
        parameters must be a date string or the value "por" which means to
        extend to the period-of-record in that direction. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional but leading zeroes are
        not; no two-digit years).

        """
        # TODO: Need to validate dates.
        if edate is None:
            if sdate.lower() == "por":  # entire period of record
                self._params["sdate"] = self._params["edate"] = "por"
            else:  # single date
                self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def __iter__(self):
        """ Stream the records from the server.

        Records will be in chronological order.

        """
        site_name, stream = self._connect()
        sid = self.meta.keys()[0]
        self.meta[sid] = {"name": site_name}
        for line in stream:
            record = [sid] + line.rstrip().split(",")
            yield record
        stream.close()
        return


class MultiStnDataStream(_CsvStream):
    """ A MultiStnData stream.

    """
    _call = WebServicesCall("MultiStnData")

    def date(self, date):
        """ Specify the date for this request.

        MultStnData only accepts a single date for CSV output. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional but leading zeroes
        are not; no two-digit years).

        """
        # TODO: Need to validate date.
        self._params["date"] = date
        return

    def location(self, **options):
        """ Set the location for this request.

        """
        # TODO: Need to validate options.
        self._params.update(options)
        return

    def __iter__(self):
        """ Stream the records from the server.

        The meta attribute will not be fully populated until every record has
        been receieved.

        """
        first_line, stream = self._connect()
        for line in itertools.chain([first_line], stream):
            record = line.rstrip().split(",")
            try:
                sid, name, state, lon, lat, elev = record[:6]
            except ValueError:  # blank line at end of output?
                break
            self.meta[sid] = {"name": name, "state": state,
                    "elev": float(elev), "ll": [float(lon), float(lat)]}
            record = [sid, self._params["date"]] + record[6:]
            yield record
        stream.close()
        return
