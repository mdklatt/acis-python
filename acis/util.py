""" ACIS utility functions.

This module contains various functions that can be used for processing ACIS
data.

"""
from .__version__ import __version__

import re

__all__ = ("sids_types",)


_SID_REGEX = re.compile(r"^([^ ]*) (\d+)$")

_SID_TYPES = {
     1: "WBAN",
     2: "COOP",
     3: "FAA",
     4: "WMO",
     5: "ICAO",
     6: "GHCN",
     7: "NWSLI",
     8: "RCC",
     9: "ThreadEx",
    10: "CoCoRaHS",
}


def sids_types(sids):
    """ Return a dict of site IDs keyed by their ID types.

    The sids parameter is a list of SIDs from ACIS metadata where each SID is
    a single string containing an identifier and its integer type code
    separated by a space, e.g. "13697 1".

    """
    types = {}
    for sid in sids:
        try:
            ident, code = _SID_REGEX.search(sid).groups()
        except AttributeError:  # search returned None
            raise ValueError("not a valid sid: {0:s}".format(sid))
        try:
            types[_SID_TYPES[int(code)]] = ident
        except KeyError:
            raise ValueError("unknown sid type: {0:s}".format(code))
    return types
