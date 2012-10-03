""" Define the correct version of uniitest.

For Python 2.6 the builtin version of unittest is replaced with unittest2, an
external library that backports Python 2.7's new unittest features to earlier
versions.

"""
import sys

if sys.version_info[1] < 7:  # Python <2.7
    import unittest2
    sys.modules["unittest"] = unittest2
