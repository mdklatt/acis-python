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
from .__version__ import __version__

from ._misc import date_params
from ._misc import valid_interval
from .call import WebServicesCall
from .error import RequestError


__all__ = ("StnMetaRequest", "StnDataRequest", "MultiStnDataRequest")


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
        """ Specify the metadata fields for this request.

        """
        self._params["meta"] = list(set(fields))  # no duplicates
        return

        
class _PlaceTimeRequest(_Request):
    """ Abstract base class for requests for spatiotemporal data.

    """
    def __init__(self):
        """ Initialize a _PlaceTimeRequest object.
        
        """
        super(_PlaceTimeRequest, self).__init__()
        return
        
    def location(self, **options):
        """ Define the location for this request.

        The options parameter is a keyword argument list defining the location
        for this request.

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
        """ Set the metadata for this request.
        
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

    def submit(self):
        """ Submit a request to the server.

        """
        # Add interval to each element before submitting request.
        for elem in self._params["elems"]:
            elem['interval'] = self._interval
        return super(_DataRequest, self).submit()

    def interval(self, value):
        """ Set the interval for this request.

        The default interval is daily.
        
        """
        self._interval = valid_interval(value)
        return

    def add_element(self, name, **options):
        """ Add an element to this request.

        """
        elem = dict([("name", name)] + options.items())
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

    def elements(self, *names):
        """ Set the elements for this request.
        
        """
        self._params["elems"] = list(names)
        return
        
        
class StnDataRequest(_StnRequest, _DataRequest):
    """ A StnData request.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location for this request.

        StnData only accepts a single "uid" or "sid" parameter.

        """
        if not set(options.keys()) < set(("uid", "sid")):
            raise RequestError("StnData requires uid or sid")
        super(StnDataRequest, self).location(**options)
        return


class MultiStnDataRequest(_StnRequest, _DataRequest):
    """ A MultiStnData request.

    """
    _call = WebServicesCall("MultiStnData")

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        MultiStnData does not accept period-of-record ("por").

        """
        if (sdate.lower() == "por" or (edate is not None and
                                                      edate.lower() == "por")):
            raise RequestError("MultiStnData does not accept POR")
        self._params.update(date_params(sdate, edate))
        return
 
 
# Development versions--not part of public interface. Testing and corresponding
# Result objects are still needed.      

class GridDataRequest(_DataRequest):
    """ A GridData request.
        
    """
    def grid(self, id):
        """ Set the grid ID for this request.
        
        """
        self._params["grid"] = id
        return
        

class GeneralRequest(_Request):
    """ A General request.
    
    """
    def __init__(self, area):
        """ Initalize a GeneralRequest object.
        
        The "id" metadata field is part of every request.
        
        """
        super(GeneralRequest, self).__init__()
        self._call = WebServicesCall("General/{0:s}".format(area))
        self._params["meta"] = "id"
        return
        
    def state(self, postal):
        """ Set the state for this request.
        
        """    
        self._params["state"] = postal
        return
        
    def metadata(self, *fields):
        """ Set the metadata for this request.
        
        """
        super(GeneralRequest, self).metadata("id", *fields)
        return
        