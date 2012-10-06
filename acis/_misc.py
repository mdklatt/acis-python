""" Miscellaneous implementation functions.

"""
from .date import date_object
from .date import date_string
from .error import RequestError


def annotate(sequence):
    """ Annotate duplicate items in a sequence to make them unique.
    
    Duplicate items will be indexed, e.g. (abc0, abc1, ...). The original order
    of the sequence is preserved, and it is returned as a tuple.
    
    """
    def counter(sequence):
        """ Replacement for collections.Counter for Python <2.7.
    
        """
        counts = {}
        for item in sequence:
            try:
                counts[item] += 1
            except KeyError:
                counts[item] = 1
        return counts

    # Reverse the sequence, then the duplicate count acts as a reverse index 
    # while successive duplicates are annotated and the count is decremented. 
    # Reverse the sequence again to restore the orignal order.
    annotated = list(reversed(sequence))
    for key, count in counter(annotated).iteritems():
        if count == 1:
            continue
        for pos, item in enumerate(annotated):
            if item != key:
                continue
            count -= 1
            annotated[pos] = "{0:s}_{1:d}".format(item, count)
    return tuple(reversed(annotated))             


def make_element(elem):
    """ Construct an element object.
    
    The elem parameter can a be an element name, a var major (vX) code, or a
    a dict. An element can have a user-specified alias assigned to the "alias"
    key if elem is a dict. Otherwise, the alias will be the element name or
    or for var major code N.
    
    """
    # This alias option is not supported by ACIS, but unknown options are
    # ignored by the server, so an element object can store arbitrary data.
    try:
        assert set(elem.iterkeys()) & set(("name", "vX"))
    except AttributeError:  # no iterkeys, string or int?
        try:
            elem = {"vX": int(elem)}
        except ValueError:  # not an integer
            elem = {"name": elem.lower()}
    if "alias" not in elem:
        try:
            elem["alias"] = elem["name"]
        except KeyError:
            elem["alias"] = "vx{0:d}".format(elem["vX"])
    return elem 
         
 
def date_params(sdate, edate=None):
    """ Define the date parameters for a call.

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


def valid_interval(value):
    """ Return a valid ACIS interval.
    
    An interval can be specified as a name ("dly", "mly", "yly") or a year,
    month, day sequence. For a sequence, only the least-signficant nonzero 
    value is used.
    
    """
    try:
        value = value.lower()
    except AttributeError:  # no lower(), not a str
        # Normalize a (y, m, d) sequence of ints.
        try:  
            yr, mo, da = (int(x) for x in value)
        except ValueError:  # not ints
            raise RequestError("invalid interval: {0:s}".format(value))
        mo = 0 if da > 0 else mo
        yr = 0 if (mo > 0 or da > 0) else yr
        value = (yr, mo, da)             
    else:
        if value not in ("dly", "mly", "yly"):
            raise RequestError("invalid interval name: {0:s}".format(value))
    return value


def date_span(params):
    """
    Determine the start date, end date, and interval for a call.
    
    If there is no end date it will None. If there is no interval it will be
    "dly".
    
    """
    try:
        sdate = params["sdate"]
    except KeyError:
        sdate = params["date"]
    edate = params.get("edate", None)
    try:
        # All elements must have the same interval, so check the first 
        # element for an interval specification.
        interval = params["elems"][0]["interval"]
    except (TypeError, KeyError): # not a sequence or no explicit interval
        interval = "dly"  # default value is daily
    return sdate, edate, interval