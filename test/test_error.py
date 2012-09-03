""" Testing for the the error.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import sys
import unittest

import localpath
from acis import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TestError(unittest.TestCase):
    """ Private base class for testing error classes.

    This class should be excluded from test discovery and execution.

    """
    def test_init(self):
        """ Test normal initialization.

        """
        message = "test error message"
        error = self.TEST_CLASS(message)
        self.assertEqual(error.message, message)
        return


class TestParameterError(_TestError):
    """ Unit testing for the ParameterError class.

    """
    TEST_CLASS = ParameterError


class TestRequestError(_TestError):
    """ Unit testing for the RequestError class.

    """
    TEST_CLASS = RequestError


class TestResultError(_TestError):
    """ Unit testing for the ResultError class.

    """
    TEST_CLASS = ResultError


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

TEST_CASES = (TestParameterError, TestRequestError, TestResultError)

def load_tests(loader, tests, pattern):
    """ Define a TestSuite for this module.

    This is part of the unittest API. The last two arguments are ignored.

    """
    suite = unittest.TestSuite()
    for test_case in TEST_CASES:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


# Make the module executable.

if __name__ == "__main__":
    sys.exit(unittest.main())
