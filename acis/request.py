""" Classes for performing an ACIS web services request.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
from . call import WebServicesCall
from . error import ParameterError 


__all__ = ("StnMetaRequest", "StnDataRequest", "MultiStnDataRequest")


class _JsonRequest(object):
    """ Private base class.

    """
    _call = WebServicesCall(None)

    def __init__(self):
        """ Initialize a request.

        """
        self._params = {"output": "json"}
        return

    def submit(self):
        """ Submit a request to the server.

        The return value is the complete query consisting of the params sent
        to the server and the result object.

        """
        return {"params": self._params, "result": self._call(self._params)}


class StnMetaRequest(_JsonRequest):
    """ A StnMeta request.

    """
    _call = WebServicesCall("StnMeta")

    def __init__(self):
        """ Initialize a StnMetaRequest object.

        """
        super(StnMetaRequest, self).__init__()
        self._params["meta"] = ["uid"]
        return

    def meta(self, *items):
        """ Specify the metadata items for this request.

        The ACIS site UID is automatically part of every request.

        """
        items = set(items)
        items.add("uid")
        self._params["meta"] = list(items)
        return

    def location(self, **options):
        """ Define the location for this request.

        """
        # Need to validate options.
        self._params.update(options)
        return


class StnDataRequest(StnMetaRequest):
    """ A StnData request.

    """
    _call = WebServicesCall("StnData")

    def __init__(self):
        """ Initialize a StnDataRequest object.

        """
        super(StnDataRequest, self).__init__()
        self._params["elems"] = []
        self._interval = "dly"
        return

    def interval(self, interval):
        """ Set the interval for this request.

        """
        if interval not in ("dly", "mly", "yly"):
            raise ParameterError("invalid interval: {s}".format(interval))
        self._interval = interval
        return

    def add_elem(self, name, **options):
        """ Add element "name" to this request with any "options".

        """
        elem = {"name": name, "interval": self._interval}
        elem.update(options)
        self._params["elems"].append(elem)
        return

    def clear_elem(self, name=None):
        """ Clear all or just "name" from the request elements.

        """
        if name is not None:
            self._params.pop(name)
        else:
            self._params["elems"] = []
        return

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        If no "edate" is specified "sdate" is treated as a single date. The
        parameters must be date string or the value "por" which means to
        extend to the period-of-record in that direction. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional; no two-digit years).

        """
        if edate is None:  # single date
            self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def location(self, **options):
        """ Set the location for this request.

        """
        if not set(options.keys()) < set(("uid", "sid")):
            raise ParameterError("StnData requires uid or sid")
        self._params.update(options)
        return


class MultiStnDataRequest(StnDataRequest):
    """ A MultiStnData request.

    """
    _call = WebServicesCall("MultiStnData")

    def __init__(self):
        """ Initialize a MultiStnDataRequest object.

        """
        super(MultiStnDataRequest, self).__init__()
        return

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        Same as StnDataRequest but "por" is not allowed.

        """
        if (sdate.lower() == "por" or edate.lower() == "por"):
            raise ParameterError("MultiStnData does not accept 'por'")
        if edate is None:  # single date
            self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def location(self, **options):
        """ Define the location for this request.

        """
        # Need to validate options.
        self._params.update(options)
        return

