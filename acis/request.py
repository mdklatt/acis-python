""" Classes for ACIS data requests.

This module provides a uniform interface for constructing an ACIS data request
and retrieving the result from the server. There is a class for each type of
web services call (StnData, MultiStnData, etc).

These classes are designed to be used with their result module counterparts,
but this is not mandatory. GridData and General calls are not currently
implemented; use a WebServicesCall instead (see the call module).

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from .call import WebServicesCall
from .error import ParameterError


__all__ = ("StnMetaRequest", "StnDataRequest", "MultiStnDataRequest")


class _JsonRequest(object):
    """ Abstract base class for all request objects.

    """
    _call = None  # child classes must set to an appropriate WebServicesCall

    def __init__(self):
        """ Initialize a request.

        """
        self._params = {"output": "json"}
        return

    def submit(self):
        """ Submit a request to the server.

        The return value is the complete query consisting of the params sent
        to the server and the result object (this can be the input for a Result
        constructor; see result.py).

        """
        return {"params": self._params, "result": self._call(self._params)}


class _MetaRequest(_JsonRequest):
    """ Abstract base class for requests with metadata.

    """
    def __init__(self):
        """ Initialize a _MetaRequest object.

        For compatibility with Result classes, the "uid" field is included by
        default (see result.py).

        """
        super(_MetaRequest, self).__init__()
        self._params["meta"] = ["uid"]
        return

    def metadata(self, *fields):
        """ Specify the metadata fields for this request.

        The fields parameter is an argument list of the desired fields. The
        "uid" field is included by default.

        """
        # TODO: Need to validate items.
        fields = set(fields)
        fields.add("uid")
        self._params["meta"] = list(fields)
        return

    def location(self, **options):
        """ Define the location for this request.

        The options parameter is a keyword argument list defining the location
        for this request.

        """
        # TODO: Need to validate options.
        self._params.update(options)
        return


class _DataRequest(_MetaRequest):
    """ Abstract base class for all requests with data.

    Data requests like StnData and MultiStnData also include metadata.

    """
    def __init__(self):
        """ Initialize a _DataRequest object.

        """
        super(_DataRequest, self).__init__()
        self._params["elems"] = []
        self._interval = "dly"
        return

    def submit(self):
        """ Submit a request to the server.

        """
        # Fully construct _params before submitting request.
        for elem in self._params['elems']:
            elem['interval'] = self._interval
        return super(_DataRequest, self).submit()

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        If no "edate" is specified "sdate" is treated as a single date. The
        parameters must be a date string or the value "por" which means to
        extend to the period-of-record in that direction. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional but leading zeroes are
        not; no two-digit years).

        """
        if edate is None:
            if sdate.lower() == "por":  # entire period of record
                self._params["sdate"] = self._params["edate"] = "por"
            else:  # single date
                self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def interval(self, interval):
        """ Set the interval for this request.

        The default interval is daily ("dly").
        """
        if interval not in ("dly", "mly", "yly"):
            raise ParameterError("invalid interval: {0:s}".format(interval))
        self._interval = interval
        return

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


class StnMetaRequest(_MetaRequest):
    """ A StnMeta request.

    """
    _call = WebServicesCall("StnMeta")


class StnDataRequest(_DataRequest):
    """ A StnData request.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location for this request.

        StnData only accepts a single "uid" or "sid" parameter.

        """
        # TODO: Need to validate options.
        if not set(options.keys()) < set(("uid", "sid")):
            raise ParameterError("StnData requires uid or sid")
        super(StnDataRequest, self).location(**options)
        return


class MultiStnDataRequest(_DataRequest):
    """ A MultiStnData request.

    """
    _call = WebServicesCall("MultiStnData")

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        MultiStnData does not accept period-of-record ("por").

        """
        # TODO: Need to validate dates.
        if (sdate.lower() == "por" or edate.lower() == "por"):
            raise ParameterError("MultiStnData does not accept por")
        super(MultiStnDataRequest, self).dates(sdate, edate)
        return
