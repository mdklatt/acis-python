""" Miscellaneous implementation functions.

"""
import collections

from .date import date_object
from .date import date_string


def annotate(sequence):
    """ Annotate duplicate items in a sequence to make them unique.
    
    Duplicate items will be indexed, e.g. (abc0, abc1, ...). The original order
    of the sequence is preserved, and it is returned as a tuple.
    
    """
    # Reverse the sequence, then the duplicate count acts as a reverse index 
    # while successive duplicates are annotated and the count is decremented. 
    # Reverse the sequence again to restore the orignal order.
    sequence = list(sequence)
    sequence.reverse()
    for key, count in collections.Counter(sequence).items():
        if not count > 1:
            continue
        for pos, item in enumerate(sequence):
            if item != key:
                continue
            count -= 1
            sequence[pos] = item + "{0:d}".format(count)
    sequence.reverse()
    return tuple(sequence)             

    
def date_params(sdate, edate=None):
    """ Set the date range (inclusive) for this request.

    If "edate" is None "sdate" is treated as a single date. The parameters must
    be a date string or "por" (period of record). Acceptable date formats are 
    YYYY-[MM-[DD]] (hyphens are optional but leading zeroes are not; no two-
    digit years).

    """
    verify = lambda s: date_string(date_object(s))
    params = {}
    if edate is None:
        if sdate.lower() == "por":  # entire period of record
            params["sdate"] = params["edate"] = "por"
        else:  # single date
            params["date"] = "por" if sdate.lower() == "por" else verify(sdate)
    else:
        params["sdate"] = "por" if sdate.lower() == "por" else verify(sdate)
        params["edate"] = "por" if edate.lower() == "por" else verify(edate)
    return params
