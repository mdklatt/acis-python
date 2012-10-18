""" Classes for ACIS data requests.

This module provides a uniform interface for constructing an ACIS data request
and retrieving the result from the server. There is a class for each type of
web services call (StnData, MultiStnData, etc).

These classes are designed to be used with their result module counterparts,
but this is not mandatory. 

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from .__version__ import __version__

from ._misc import date_params
from ._misc import make_element
from ._misc import valid_interval
from .call import WebServicesCall
from .error import RequestError


__all__ = ("StnMetaRequest", "StnDataRequest", "MultiStnDataRequest",
           "GridDataRequest", "AreaMetaRequest")


class _Request(object):
    """ Abstract base class for all request objects.

    """
    # Child classes must define this as an appropriate WebServicesCall (or
    # equivalent). It can be either a class or object attribute/method as
    # needed.
    _call = None

    def __init__(self):
        """ Initialize a _Request object.

        """
        self._params = {}
        return

    def submit(self):
        """ Submit a request to the server.

        The return value is the complete query consisting of the params sent
        to the server and the result object (this can be the input for a Result
        constructor; see result.py).

        """
        return {"params": self._params, "result": self._call(self._params)}

    def metadata(self, *fields):
        """ Set the metadata fields for this request.

        """
        self._params["meta"] = tuple(set(fields))  # no duplicates
        return

    @property
    def params(self):
        """ Read-only access to _params.
        
        """
        return self._params
        

class _PlaceTimeRequest(_Request):
    """ Abstract base class for spatiotemporal data reuests.

    """
    def location(self, **options):
        """ Define the location options for this request.

        """
        self._params.update(options)
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


class _StnRequest(_PlaceTimeRequest):
    """ Abstract base class for station (meta)data requests.

    For compatibility with Result classes the "uid" metadata field is part of
    every request (see result.py).

    """
    def __init__(self):
        """ Initialize a _SiteRequest object.

        """
        super(_StnRequest, self).__init__()
        self._params["meta"] = ["uid"]
        return

    def metadata(self, *fields):
        """ Set the metadata fields for this request.

        """
        super(_StnRequest, self).metadata("uid", *fields)
        return


class _DataRequest(_PlaceTimeRequest):
    """ Abstract base class for all meteorological data requests.

    """
    def __init__(self):
        """ Initialize a _DataRequest object.

        """
        super(_DataRequest, self).__init__()
        self._params["elems"] = []
        self._interval = "dly"
        return

    def interval(self, value):
        """ Set the interval for this request.

        The default interval is daily.

        """
        self._interval = valid_interval(value)
        for elem in self._params["elems"]:
            elem['interval'] = self._interval
        return

    def add_element(self, ident, **options):
        """ Add an element to this request.

        If ident is an integer (literal or string) it will be treated as a
        var major (vX) specifier.

        """
        elem = make_element(ident)
        options["interval"] = self._interval
        elem.update(options)
        self._params["elems"].append(elem)
        return

    def clear_elements(self):
        """ Clear all elements from this request.

        """
        self._params["elems"] = []
        return


class StnMetaRequest(_StnRequest):
    """ A StnMeta request.

    """
    _call = WebServicesCall("StnMeta")

    def elements(self, *idents):
        """ Set the elements for this request.

        """
        self._params["elems"] = tuple(map(make_element, idents))
        return


class StnDataRequest(_StnRequest, _DataRequest):
    """ A StnData request.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location options for this request.

        StnData only accepts a single "uid" or "sid" parameter.

        """
        if not set(options.iterkeys()) < set(("uid", "sid")):
            raise RequestError("StnData requires uid or sid")
        super(StnDataRequest, self).location(**options)
        return


class MultiStnDataRequest(_StnRequest, _DataRequest):
    """ A MultiStnData request.

    """
    _call = WebServicesCall("MultiStnData")

    def dates(self, sdate, edate=None):
        """ Set the date range (inclusive) for this request.

        MultiStnData does not accept period-of-record ("por").

        """
        if (sdate.lower() == "por" or (edate is not None and
                                                      edate.lower() == "por")):
            raise RequestError("MultiStnData does not accept POR")
        self._params.update(date_params(sdate, edate))
        return


class GridDataRequest(_DataRequest):
    """ A GridData request.

    """
    _call = WebServicesCall("GridData")

    def grid(self, id):
        """ Set the grid ID for this request.

        """
        self._params["grid"] = id
        return

    def dates(self, sdate, edate=None):
        """ Set the date range (inclusive) for this request.

        GridData does not accept period-of-record ("por").

        """
        if (sdate.lower() == "por" or (edate is not None and
                                                      edate.lower() == "por")):
            raise RequestError("GridData does not accept POR")
        self._params.update(date_params(sdate, edate))
        return


class AreaMetaRequest(_Request):
    """ A General request for area metadata.

    """
    def __init__(self, area):
        """ Initalize an AreaMetaRequest object.

        The "id" metadata field is part of every request.

        """
        super(AreaMetaRequest, self).__init__()
        self._call = WebServicesCall("General/{0:s}".format(area))
        self._params["meta"] = "id"
        return

    def state(self, *postal):
        """ Set the state(s) for this request.

        """
        self._params["state"] = postal
        return

    def metadata(self, *fields):
        """ Set the metadata fields for this request.

        For compatibility with AreaMetaResult the id field is requested by
        default (see result.py).

        """
        super(AreaMetaRequest, self).metadata("id", *fields)
        return
