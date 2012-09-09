""" Set up the test environment.

The working directory is changed to the test directory and the module search
path is modified so that the local version of the library is imported.

"""
import os
import sys

_TEST_PATH = os.path.dirname(__file__)
_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")

os.chdir(_TEST_PATH)
sys.path.insert(0, _ROOT_PATH)
