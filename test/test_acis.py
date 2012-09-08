""" The master test script for the acis package.

This script runs all tests in this directory.
"""
import os
import sys
import unittest

def main(argv):
    """ Run all tests in this directory.

    The test directory is searched for all test scripts ('test_*.py'), and all
    the unit tests (TestCase implementations) they contain are run as a single
    test suite.
    """
    path = os.path.join(os.path.dirname(__file__))
    suite = unittest.defaultTestLoader.discover(path, "test_*.py")
    result = unittest.TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


# Make the script executable.

if __name__ == "__main__":
    sys.exit(main(sys.argv))
