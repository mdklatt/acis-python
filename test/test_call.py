""" Testing for the the call.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import unittest

import _env
from acis.call import *
from acis.error import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class WebServicesCallTest(unittest.TestCase):
    """ Unit testing for the WebServicesCall class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self._call = WebServicesCall("StnData")
        return

    def test_url(self):
        """ Test the url attribute.

        """
        self.assertEqual(self._call.url, "http://data.rcc-acis.org/StnData")
        return

    def test_call(self):
        """ Test a normal call.

        """
        params = {"sid": "okc", "date": "2012-01-01", "elems": "maxt",
                  "meta": "uid"}
        result = {"meta": {"uid":92}, "data": [["2012-01-01","50"]]}
        self.assertDictEqual(self._call(params), result)
        return

    def test_error(self):
        """ Test a call with invalid parameters.

        """
        with self.assertRaises(RequestError) as context:
            self._call({})
        self.assertEqual(context.exception.message, "Need sId")
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (WebServicesCallTest,)

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
