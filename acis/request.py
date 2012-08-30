""" Classes for performing an ACIS web services request.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
__version__ = "0.1.dev"

import json
import re
import urllib
import urlparse

__all__ = ("Request", "StnMetaRequest", "StnDataRequest",
    "MultiStnDataRequest", "RequestError", "ParameterError")


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

    def __init__(self, req_type):
        """ Initialize a request.

        The 'req_type' parameter is the type of ACIS request, e.g. 'StnMeta',
        'StnData', etc.

        """
        self.url = urlparse.urljoin(Request.SERVER, req_type)
        return

    def submit(self, params):
        """ Submit a request to the server.

        The 'params' parameter is a dict specifying the request parameters. The
        return value is a dict containing the input parameters and the deocded
        JSON object returned by the server.

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
        return {"params": params, "result": json.loads(conn.read())}


class _MetaRequest(Request):
    """ Private request for site metadata requests.

    """
    def __init__(self, req_type):
        """ Initialize a _MetaRequest object.

        """
        Request.__init__(self, req_type)
        self.params = {"meta": ["uid"]}
        return

    def get(self):
        return Request.get(self, self.params)

    def meta(self, *args):
        self.params["meta"] += filter(lambda x: x != "uid", args)
        return

    def location(self, **kwargs):
        self.params.update(kwargs)
        return


class _DataRequest(_MetaRequest):
    """ Private base class for site data requests.

    """
    def __init__(self, req_type):
        """ Initialize a _DataRequest object.

        """
        _MetaRequest.__init__(self, req_type)
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

    def element(self, name, **kwargs):
        """ Add an element to this request.

        """
        elem = {"name": name, "interval": self._interval}
        elem.update(kwargs)
        self.params["elems"].append(elem)
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
        _MetaRequest.__init__(self, "StnMeta")
        return


class StnDataRequest(_DataRequest):
    """ A StnData request.

    """
    def __init__(self):
        """ Initialize a StnDataRequest object.

        """
        _DataRequest.__init__(self, "StnData")
        return

    def location(self, uid=None, sid=None):
        """ Set the location for this request.

        """
        if uid is not None:
            self.params['uid'] = int(uid)
        elif sid is not None:
            self.params['sid'] = str(sid)
        else:
            raise ParameterError('uid and sid cannot both be None')
        return


class MultiStnDataRequest(_DataRequest):
    """ A MultiStnData request.

    """
    def __init__(self):
        _DataRequest.__init__(self, "MultiStnData")
        return


class RequestError(Exception):
    """ The server reported that the request was invalid.

    """
    pass


class ParameterError(Exception):
    """ The request parameters are not correct.

    """
    pass
