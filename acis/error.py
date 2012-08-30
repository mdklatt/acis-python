""" Exception classes for the ACIS package.

"""
__version__ = "0.1.dev"


__all__ = ("RequestError", "ResultError", "ParameterError")


class RequestError(Exception):
    """ The server reported that the request was invalid.

    The ACIS server returned an HTTP status code of 400 indicating that it
    could not complete the request due to an invalid 'params' object.

    """
    pass


class ResultError(Exception):
    """ An error reported by the ACIS result object.

    The server returned an object, but it is invalid. The object will contain
    an 'error' key with a string describing the error.

    """
    pass


class ParameterError(Exception):
    """ The request parameters are not correct.

    """
    pass
