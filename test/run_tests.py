""" Master test script.

"""
import os.path
import sys

import _unittest as unittest

def main(argv=None):
    """ Run all tests in this directory.

    The test directory is searched for all test scripts ('test_*.py'), and all
    the unit tests they contain are run as a single test suite.
    
    """
    path = os.path.join(os.path.dirname(__file__))
    suite = unittest.defaultTestLoader.discover(path, "test_*.py")
    result = unittest.TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


# Make the script executable.

if __name__ == "__main__":
    sys.exit(main(sys.argv))
