""" Set up the test path.

The working directory is changed to the test directory and the module search
path is modified so that the local version of the library is imported. For 
Python 2.6 the builtin version of unittest is replaced with unittest2, an
external library that backports Python 2.7's new unittest features to earlier
versions.

"""
import os
import sys

_TEST_PATH = os.path.dirname(__file__)
_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
os.chdir(_TEST_PATH)
sys.path.insert(0, _ROOT_PATH)
if sys.version_info[1] < 7:  # Python <2.7
    import unittest2
    sys.modules["unittest"] = unittest2
