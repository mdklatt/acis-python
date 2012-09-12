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


class _MetaRequest(_JsonRequest):
    """

    """
    def __init__(self):
        """ Initialize a _MetaRequest object.

        """
        super(_MetaRequest, self).__init__()
        self._params["meta"] = ["uid"]
        return

    def metadata(self, *items):
        """ Specify the metadata items for this request.

        The ACIS site UID is automatically part of every request.

        """
        # TODO: Needd to validate items.
        items = set(items)
        items.add("uid")
        self._params["meta"] = list(items)
        return

    def location(self, **options):
        """ Define the location for this request.

        """
        # TODO: Need to validate options.
        self._params.update(options)
        return


class _DataRequest(_MetaRequest):

    def __init__(self):
        """ Initialize a _DataRequest object.

        """
        super(_DataRequest, self).__init__()
        self._params["elems"] = []
        self._interval = "dly"
        return

    def submit(self):
        """ Submit a request to the server.

        The return value is the complete query consisting of the params sent
        to the server and the result object.

        """
        # Add interval to each element.
        for elem in self._params['elems']:
            elem['interval'] = self._interval
        return super(_DataRequest, self).submit()

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        If no "edate" is specified "sdate" is treated as a single date. The
        parameters must be date string or the value "por" which means to
        extend to the period-of-record in that direction. Acceptable date
        formats are YYYY-[MM-[DD]] (hyphens are optional; no two-digit years).

        """
        if edate is None:
            if sdate.lower() == "por":  # entire period of record
                self.params["sdate"] = self.params["edate"] = "por"
            else:  # single date
                self._params["date"] = sdate
        else:
            self._params["sdate"] = sdate
            self._params["edate"] = edate
        return

    def interval(self, interval):
        """ Set the interval for this request.

        """
        if interval not in ("dly", "mly", "yly"):
            raise ParameterError("invalid interval: {s}".format(interval))
        self._interval = interval
        return

    def add_element(self, name, **options):
        """ Add element "name" to this request with any "options".

        """
        # TODO: Check if "name" already exists before adding.
        elem = dict([("name", name)] + options.items())
        self._params["elems"].append(elem)
        return

    def del_element(self, name=None):
        """ Clear all or just "name" from the element list.

        """
        if name is None:
            self._params["elems"] = []
        elems = self._params["elems"]
        for pos, elem in enumerate(elems):
            if elem["name"] == name:
                elems.pop(pos)
                break
        return


class StnMetaRequest(_MetaRequest):
    """ A StnMeta request.

    """
    _call = WebServicesCall("StnMeta")


class StnDataRequest(_DataRequest):
    """ A StnData request.

    """
    _call = WebServicesCall("StnData")

    def location(self, **options):
        """ Set the location for this request.

        """
        # More restrictive parameters.
        if not set(options.keys()) < set(("uid", "sid")):
            raise ParameterError("StnData requires uid or sid")
        super(StnDataRequest, self).location(**options)
        return


class MultiStnDataRequest(_DataRequest):
    """ A MultiStnData request.

    """
    _call = WebServicesCall("MultiStnData")

    def dates(self, sdate, edate=None):
        """ Specify the date range (inclusive) for this request.

        """
        # More restrictive parameters.
        if (sdate.lower() == "por" or edate.lower() == "por"):
            raise ParameterError("MultiStnData does not accept 'por'")
        super(MultiStnDataRequest, self).dates(sdate, edate)
        return
