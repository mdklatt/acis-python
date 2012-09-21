""" Testing for the the error.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import unittest

import _env
from acis import RequestError
from acis import ResultError


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _ErrorTest(unittest.TestCase):
    """ Private base class for testing error classes.

    This class should be excluded from test discovery and execution. Derived
    classes must define the _class attribute.

    """
    _class = None

    def test_init(self):
        """ Test normal initialization.

        """
        message = "test error message"
        error = self._class(message)
        self.assertEqual(error.message, message)
        return


class RequestErrorTest(_ErrorTest):
    """ Unit testing for the RequestError class.

    """
    _class = RequestError


class ResultErrorTest(_ErrorTest):
    """ Unit testing for the ResultError class.

    """
    _class = ResultError


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (RequestErrorTest, ResultErrorTest)

def load_tests(loader, tests, pattern):
    """ Define a TestSuite for this module.

    This is part of the unittest API. The last two arguments are ignored. The
    _TEST_CASES global is used to determine which TestCase classes to load
    from this module.

    """
    suite = unittest.TestSuite()
    for test_case in _TEST_CASES:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


# Make the module executable.

if __name__ == "__main__":
    unittest.main()  # main() calls sys.exit()
