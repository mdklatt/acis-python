"""

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
import json
import urllib
import urllib2
import urlparse

from . error import RequestError

__all__ = ("WebServicesCall",)

class WebServicesCall(object):
    """ An ACIS Web Services call.

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
        return depends on the output type specified in params. JSON output
	(the) default gets decoded and returned as a dict and for all other
	output types a stream object gets returned. 

        """
        stream = self._post(urllib.urlencode({"params": json.dumps(params)}))
        try:
            if params["output"].lower() != "json":
                return stream
        except KeyError:  # no response specified, JSON is default
            pass
        try:
            return json.loads(stream.read())
        except ValueError:
            raise ValueError("server did not return valid JSON object")


    def _post(self, data):
        """ Execute a POST request.

        """
        HTTP_BAD = 400
        try:
            stream = urllib2.urlopen(urllib2.Request(self.url, data))
        except urllib2.HTTPError as err:
            # This doesn't do the right thing for a "soft 404", e.g. an ISP
            # redirects to a custom error or search page for a DNS lookup
            # failure and returns a 200 (OK) code.
            if err.code == HTTP_BAD:  # plaint text error from ACIS server
                raise RequestError(err.read().strip())
            else:
                raise
        return stream
