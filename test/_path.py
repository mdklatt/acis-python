""" Set up the test path.

The module search path is modified so that the local version of the library is 
imported.

"""
from os.path import join
from os.path import dirname
from sys import path

_ROOT_PATH = join(dirname(__file__), "..")
path.insert(0, _ROOT_PATH)
