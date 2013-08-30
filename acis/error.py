""" Exception classes for the acis library.

All exception classes should be defined in this module.

"""
__all__ = ("Error", "RequestError", "ResultError")


class Error(Exception):
    """ The base class for all acis exceptions.

    """
    pass


class RequestError(Exception):
    """ An invalid request.

    """
    pass


class ResultError(Error):
    """ An invalid result.

    """
    pass
