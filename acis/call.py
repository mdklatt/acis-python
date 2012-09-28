""" Execute ACIS Web Services calls.

This is the core library module. The WebServicesCall is all that is needed to
execute an ACIS Web Services call, and can be uses in cases where the Request,
Result, or Stream classes do not have the needed functionality. In particular,
a WebServicesCall is necessary for GridData and General calls.

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from .__version__ import __version__

import contextlib
import json
import urllib
import urllib2
import urlparse

from .error import RequestError
from .error import ResultError

__all__ = ("WebServicesCall",)


class WebServicesCall(object):
    """ An ACIS Web Services call.

    This class handles the encoding of the params object, the HTTP request and
    error handling, and decoding of the returned result.

    """
    _SERVER = "http://data.rcc-acis.org"

    def __init__(self, call_type):
        """ Initialize a WebServicesCall.

        The call_type parameter is the type of ACIS call, e.g. "StnMeta",
        "StnData", etc.

        """
        self.url = urlparse.urljoin(self._SERVER, call_type)
        return

    def __call__(self, params):
        """ Execute a web services call.

        The params parameter is a dict specifying the call parameters. The
        result depends on the output type specified in params. JSON output
        (the default) gets decoded and returned as a dict, and for all other
        output types a stream object gets returned.

        """
        stream = self._post(urllib.urlencode({"params": json.dumps(params)}))
        if params.get("output", "json").lower() != "json":
            return stream
        try:
            result = json.loads(stream.read())
        except ValueError:
            raise ResultError("server returned invalid JSON")
        finally:
            stream.close()
        return result

    def _post(self, data):
        """ Execute a POST request.

        The data parameter must be a properly encoded and escaped string.

        """
        HTTP_BAD = 400
        try:
            stream = urllib2.urlopen(urllib2.Request(self.url, data))
        except urllib2.HTTPError as err:
            # This doesn't do the right thing for a "soft 404", e.g. an ISP
            # redirects to a custom error or search page for a DNS lookup
            # failure and returns a 200 (OK) code.
            if err.code == HTTP_BAD:
                # If the ACIS server returns this code it also provides a
                # helpful plain text error message as the content.
                raise RequestError(err.read().rstrip())
            else:
                raise
        return stream
