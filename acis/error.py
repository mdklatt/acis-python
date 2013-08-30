""" Exception classes for the acis library.

"""
__all__ = ("RequestError", "ResultError")


class RequestError(Exception):
    """ An invalid request.

    """
    pass


class ResultError(Exception):
    """ An invalid result.

    """
    pass
