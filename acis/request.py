""" Classes for performing an ACIS web services request.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
__version__ = "0.1.dev"

import json
import re
import urllib
import urlparse

from error import *
from result import *


__all__ = ("Request", "StnMetaRequest", "StnDataRequest",
    "MultiStnDataRequest")


def _date_string(date):
    """ Return an ACIS-format date string.

    Call strftime() or return a string as-is.
    """
    # Use dateutil.parser to validate date strings?
    try:  # c.f. datetime.date and datetime.datetime
        date = date.strftime("%Y%m%d")
    except AttributeError:  # no strftime
        pass
    return str(date)


class Request(object):
    """ A generic ACIS request.

    """
    SERVER = "http://data.rcc-acis.org"

    def __init__(self, query_type):
        """ Initialize a request.

        The 'query_type' parameter is the type of ACIS query, e.g. 'StnMeta',
        'StnData', etc.

        """
        self.url = urlparse.urljoin(Request.SERVER, query_type)
        return

    def submit(self, params):
        """ Submit a request to the server.

        The 'params' parameter is a dict specifying the request parameters. The
        return value is a dict containing the decoded JSON object returned by
        the server.

        """
        HTTP_OK = 200
        HTTP_BAD = 400
        query = urllib.urlencode({"params": json.dumps(params)})
        conn = urllib.urlopen(self.url, query)  # POST request
        code = conn.getcode()
        if code != HTTP_OK:
            # This doesn't do the right thing for a "soft 404", e.g. an ISP
            # redirects to a custom error or search page for a DNS lookup
            # failure. If that happens expect a ValueError from json.loads().
            if code == HTTP_BAD:  # ACIS plain text error message
                raise RequestError(conn.read());
            else:  # not an ACIS request error
                raise RuntimeError("HTTP error %d" % code)
        result = json.loads(conn.read())
        try:
            raise ResultError(result["error"])
        except KeyError:  # no error
            return result


class _ParamRequest(Request):
    """ Private base class for advanced Request types.

    A _ParamRequest facilitates the creation of and maintains its own 'params'
    object.

    """
    def __init__(self, query_type, result_cls):
        """ Initialize a _ParamRequest object.

        The 'query_type' parameter is the type of ACIS query, e.g. 'StnMeta',
        'StnData', etc. The 'reslt_cls' parameter is the type of result
        (StnMetaResult, StnDataResult, etc.) returned by this request.

        """
        super(_ParamRequest, self).__init__(query_type)
        self._result_cls = result_cls
        self.params = {}
        return

    def submit(self):
        """ Return the result of this request.

        The return value is a result object appropriate to the request type.
        """
        result = Request.submit(self, self.params)
        return self._result_cls(self.params, result)


class _MetaRequest(_ParamRequest):
    """ Private base class for retrieving metadata.

    """
    def __init__(self, query_type, result_cls):
        """

        """
        super(_MetaRequest, self).__init__(query_type, result_cls)
        self.params["meta"] = ("uid",)
        return

    def meta(self, *args):
        """ Define the 'meta' parameter for this request.

        The ACIS site UID is automatically part of every request.

        """
        args = set(args)
        args.add("uid")
        self.params["meta"] = list(args)
        return

    def location(self, **kwargs):
        """ Define the location for this request.

        """
        self.params.update(kwargs)
        return


class _DataRequest(_ParamRequest):
    """ Private base class for retrieving data.

    """
    def __init__(self, query_type, result_cls):
        """ Initialize a _DataRequest object.

        """
        super(_DataRequest, self).__init__(query_type, result_cls)
        self.params["elems"] = []
        self._interval = "dly"
        return

    def interval(self, interval):
        """ Set the interval for this request.

        """
        if interval not in ("dly", "mly", "yly"):
            raise ParameterError("invalid interval: %s" % interval)
        self._interval = interval
        return

    def add_element(self, name, **kwargs):
        """ Add an element to this request.

        """
        elem = {"name": name, "interval": self._interval}
        elem.update(kwargs)
        self.params["elems"].append(elem)
        return

    def clear_elements(self):
        """ Clear all elements from this request.

        """
        self.params["elems"] = []
        return

    def dates(self, sdate, edate=None):
        """ Set the date range for this request.

        Dates can be specified as datetime objects or strings that are in
        an ACIS-acceptable format (YYYY[-MM[-DD]
        """
        if edate is None:  # single date
            self.params["date"] = _date_string(sdate)
        else:
            self.params["sdate"] = _date_string(sdate)
            self.params["edate"] = _date_string(edate)
        return


class StnMetaRequest(_MetaRequest):
    """ A StnMeta request.

    """
    def __init__(self):
        """ Initialize a StnMetaRequest object.

        """
        super(StnMetaRequest, self).__init__("StnMeta", StnMetaResult)
        return


class StnDataRequest(_MetaRequest, _DataRequest):
    """ A StnData request.

    """
    def __init__(self):
        """ Initialize a StnDataRequest object.

        """
        super(StnDataRequest, self).__init__("StnData", StnDataResult)
        return

    def location(self, uid=None, sid=None):
        """ Set the location for this request.

        """
        if uid is not None:
            self.params["uid"] = int(uid)
        elif sid is not None:
            self.params["sid"] = str(sid)
        else:
            raise ParameterError("must specify uid or sid")
        return


class MultiStnDataRequest(_MetaRequest, _DataRequest):
    """ A MultiStnData request.

    """
    def __init__(self):
        """ Initialize a MultiStnDataRequest object.

        """
        super(MultiStnDataRequest, self).__init__("MultiStnData",
            MultiStnDataResult)
        return
