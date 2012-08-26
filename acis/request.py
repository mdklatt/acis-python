"""
Classes for performing an ACIS data request.

"""
__version__ = '0.1.dev'
__all__ = ('Request', 'RequestError')

import json
import re
import urllib
import urlparse


class Request(object):
    """
    A generic ACIS request.

    """
    SERVER = 'http://data.rcc-acis.org'

    def __init__(self, action):
        self._url = urlparse.urljoin(Request.SERVER, action)
        return

    def submit(self, params):
        """
        Request the data defined by 'params' from the server.

        The return value is a dict containing the input parameters and the
        the decoded JSON result returned by the server.
        """
        HTTP_OK = 200
        query = urllib.urlencode({ 'params': json.dumps(params) })
        conn = urllib.urlopen(self._url, data=query)  # POST request
        code = conn.getcode()
        if code != HTTP_OK:
            raise RequestError(conn.read(), code)
        result = json.loads(conn.read())
        return { 'params': params, 'result': result }


class RequestError(Exception):
    """
    The server was unable to process the request.

    This is reported as an HTTP status other than OK. In addition to the usual
    HTTP errors, this will occur if the server could not parse the request. The
    'code' attribute contains the HTTP status code.
    """
    def __init__(self, message, code):

        # message might be HTML; extract text from <p>...</p>
        regex = r'<html>[\s\S]*<p>([\s\S]*)</p>'
        try:
            message = re.search(regex, message).group(1)
        except AttributeError:  # match is None, plain text
            pass
        Exception.__init__(self, message)
        self.code = code
        return
