""" Miscellaneous ACIS utility functions.

"""
__version__ = "0.1.dev"

import re

__all__ = ("decode_sids",)


_SID_REGEX = re.compile(r"(^[^ ]*) (\d+)$")

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


def decode_sids(sids):
    """ Return a dict of site IDs keyed by their decoded ID types.

    The 'sids' parameter is a list of SIDs from ACIS metadata where each SID is
    a single string containing an identifier and its integer type code
    separated by a space.

    """
    decoded = {}
    for sid in sids:
        try:
            ident, code = _SID_REGEX.search(sid).groups()
        except AttributeError:  # search returned None
            raise ValueError("not a valid sid: %s" % sid)
        try:
            decoded[_SID_TYPES[int(code)]] = ident
        except KeyError:
            raise ValueError("unknown sid type: %s" % code)
    return decoded
