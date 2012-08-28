""" Classes for performing an ACIS web services request.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
__version__ = "0.1.dev"

import json
import re
import urllib
import urlparse

__all__ = ("Request", "RequestError")


class Request(object):
    """ A generic ACIS request.

    """
    SERVER = "http://data.rcc-acis.org"

    def __init__(self, action):
        """ Initialize a request.

        The 'action' parameter specifies the type of request, i.e. StnMeta,
        StnData, etc.

        """
        self.url = urlparse.urljoin(Request.SERVER, action)
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


class RequestError(Exception):
    """ The server reported that the request was invalid.

    """
    pass
