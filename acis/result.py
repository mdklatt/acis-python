""" Classes for working with an ACIS web services result object.

This implementation is based on ACIS Web Services Version 2:
<http://data.rcc-acis.org/doc/>.

"""
__version__ = "0.1.dev"

import collections
import itertools

from . error import *
from . date import *

__all__ = ("StnMetaResult", "StnDataResult", "MultiStnDataResult")


class _JsonResult(object):
    """ Base class for all result objects.

    """
    def __init__(self, query):
        result = query["result"]
        try:
            raise result["error"]
        except KeyError:  # no error
            pass
        return;


class StnMetaResult(_JsonResult):
    """ A StnMeta result for one or more sites.

    The 'meta' attribute is a dict keyed to ACIS site uid(s).

    """
    def __init__(self, query):
        """ Initialize a StnMetaResult object.

        The query parameter is a dict containing the params sent to the server
        and the result it return. The result must contain the uid metadata
        item.

        """
        meta = query["result"]["meta"]
        try:
            self.meta = {site.pop("uid"): site for site in meta}
        except KeyError:
            raise ParameterError("uid is a required meta element")
        return


class _DataResult(_JsonResult):
    """ Base class for a station data result.

    _DataResult objects have a 'data' and 'meta' attribute corresponding to
    the data and metadata in the ACIS result object. Each attribute is a dict
    keyed to ACIS site uid(s) so the ACIS result must contain the 'uid'
    metadata element.

    """
    def __init__(self, query):
        """ Initialize a _DataResult object.

        """
        super(_DataResult, self).__init__(query)
        self.data = {}
        self.meta = {}
        elems = query["params"]["elems"]
        try:
            # a comma-delimited string
            self.fields = [elem.strip() for elem in elems.split(",")]
        except AttributeError:  # no split(), not a string
            try:
                # a sequence of dicts
                self.fields = [elem["name"] for elem in elems]
            except TypeError:  # no string indices, not a dict
                # a sequence of strings
                self.fields = elems
        return

    def __len__(self):
        """ Return the number of data records in this result.

        """
        count = 0
        for uid in self.data:
            count += len(self.data[uid])
        return count


class StnDataResult(_DataResult):
    """ A StnData result for a single site.

    """
    def __init__(self, query):
        """ Initialize a StnDataResult object.

        The query parameter is a dict containing the params sent to the server
        and the result it return. The result must contain the uid metadata
        item.

        """
        super(StnDataResult, self).__init__(query)
        result = query["result"]
        try:
            uid = result["meta"].pop("uid")
        except KeyError:
            raise ParameterError("uid is a required meta element")
        self.meta = {uid: result["meta"]}
        self.data = {uid: result["data"]}
        smry = result.get("smry", [])
        self.smry = {uid: collections.OrderedDict(zip(self.fields, smry))}
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).

        """
        fields = ["uid", "date"] + self.fields
        for uid, data in self.data.items():
            for record in data:
                record.insert(0, uid)
                yield collections.OrderedDict(zip(fields, record))
        return


class MultiStnDataResult(_DataResult):
    """ A MultiStnData result for one more sites.

    """
    def __init__(self, query):
        """ Initialize a MultiStnDataResult object.

        The query parameter is a dict containing the params sent to the server
        and the result it return. The result must contain the uid metadata
        item.

        """
        super(MultiStnDataResult, self).__init__(query)
        self.meta = {}
        self.data = {}
        self.smry = {}
        for site in query["result"]["data"]:
            try:
                uid = site["meta"].pop("uid")
            except KeyError:
                raise ParameterError("uid is a required meta element")
            self.meta[uid] = site["meta"]
            self.data[uid] = site["data"]
            try:
                smry = site["smry"]
            except KeyError:  # no "smry"
                continue
            self.smry[uid] = collections.OrderedDict(zip(self.fields, smry))
        self._dates = date_range(query["params"])
        return

    def __iter__(self):
        """ Iterate over each data record in the result.

        Each record is a tuple: (uid, date, elem1, ...).  This currently does
        not work for elements with a 'groupby' specification.

        """
        fields = ["uid", "date"] + self.fields
        date_iter = itertools.cycle(self._dates)
        for uid, data in self.data.items():
            for record in data:
                record.insert(0, uid)
                record.insert(1, date_iter.next())
                yield collections.OrderedDict(zip(fields, record))
        return
