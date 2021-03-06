""" ACIS utility functions.

This module contains various functions that can be useful for processing ACIS
data.

The array_result function (optional) requires the numpy library: 
    <http://numpy.scipy.org/>

This implementation is based on ACIS Web Services Version 2:
    <http://data.rcc-acis.org/doc/>.

"""
from __future__ import absolute_import

from re import compile

__all__ = ("decode_sids", "result_array")


def decode_sids(sids):
    """ Return a dict of site IDs keyed by their network types.

    The parameter is a list of SIDs from ACIS metadata where each SID is a
    single string containing an identifier and its network type separated by a
    space, e.g. "13697 1". There can be more than one ID per network.

    """
    table = {}
    for sid in sids:
        try:
            ident, ntype = sid.split()
            ntype = int(ntype)
        except ValueError:  # not enough items in split or int() failed
            raise ValueError("invalid SID: {0:s}".format(sid))
        network = decode_sids._networks.get(ntype, ntype)
        table.setdefault(network, list()).append(ident)
    return table

decode_sids._regex = compile(r"^([^ ]*) (\d+)$")
decode_sids._networks = {
     1: "WBAN",      2: "COOP",      3: "FAA",       4: "WMO", 
     5: "ICAO",      6: "GHCN",      7: "NWSLI",     8: "RCC",  
     9: "ThreadEx", 10: "CoCoRaHS", 16: "AWDN",     29: "SNOTEL"}


try:
    import numpy
except ImportError:
    pass
else:
    # Define function if numpy is available.
    def result_array(result):
        """ Convert a data result to a numpy record array.
    
        """
        # Element names are converted to plain strings because numpy does
        # not play well with Unicode.
        elems = [(str(elem), object) for elem in result.elems]
        dtype = [("uid", int), ("date", str, 10)] + elems
        return numpy.array([tuple(record) for record in result], dtype)
