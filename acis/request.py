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

        The 'params' input is a dict specifying the request parameters. The
        return value is a dict containing the input parameters and the deocded
        JSON object returned by the server.

        """
        HTTP_OK = 200
        data = urllib.urlencode({"params": json.dumps(params)})
        conn = urllib.urlopen(self.url, data)  # POST request
        code = conn.getcode()
        if code != HTTP_OK:
            raise RequestError(conn.read(), code)
        result = json.loads(conn.read())
        return {"params": params, "result": result}


class RequestError(Exception):
    """ An error reported by the server.

    The server was unable to complete the request and reported as an HTTP
    status code other than OK. In addition to the usual HTTP errors the server
    will report an error if the request parameters are invalid. The 'code'
    attribute contains the returned HTTP status code.

    """
    def __init__(self, message, code):
        # message might be HTML; extract text from <p>...</p>
        regex = r"<html>[\s\S]*<p>([\s\S]*)</p>"
        try:
            message = re.search(regex, message).group(1)
        except AttributeError:  # match is None, plain text
            pass
        Exception.__init__(self, message)
        self.code = code
        return
