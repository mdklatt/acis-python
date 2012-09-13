""" Exception classes for the acis library.

All exception classes should be defined in this module.

"""
from .__version__ import __version__

__all__ = ("Error", "RequestError", "ResultError", "ParameterError")


class Error(Exception):
    """ The base class for all acis libary exceptions.

    This class provides the standard Exception functionality.
    """
    pass


class RequestError(Error):
    """ The server reported that the request was invalid.

    The ACIS server returned an HTTP status code of 400 indicating that it
    could not complete the request due to an invalid 'params' object.

    """
    pass


class ResultError(Error):
    """ An error reported by the ACIS result object.

    The server returned an object, but it is invalid. The object will contain
    an "error" key with a string describing the error.

    """
    pass


class ParameterError(Exception):
    """ The call parameters are not correct.

    """
    pass
