""" Compatibility wrapper for the unittest library.

For Python 2.6 the builtin version of unittest is replaced with unittest2, an
external library that backports Python 2.7 unittest features.

"""
from sys import version_info

if version_info[1] >= 7:  # Python 2.7+
    from unittest import *
else: 
    from unittest2 import *
