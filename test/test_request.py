""" Testing for the the request.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import json
import unittest

import _env
from acis.request import *

# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _RequestTest(unittest.TestCase):
    """ Private base class for testing request classes.

    This class should be excluded from test discovery and execution. Child
    classes must define the _JSON_FILE and _TEST_CLASS class attributes.

    """
    _JSON_FILE = None
    _TEST_CLASS = None

    @classmethod
    def load_json(cls):
        """ Load the JSON test data.

        """
        return json.load(open(cls._JSON_FILE, "r"))

    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        test_data = self.load_json()
        params = test_data["params"]
        result = test_data["result"]
        self.query = {"params": params, "result": result}
        self.request = self._TEST_CLASS()
        return


class StnMetaRequestTest(_RequestTest):
    """ Unit testing for the StnMetaRequest class.

    """
    _JSON_FILE = "data/StnMeta.json"
    _TEST_CLASS = StnMetaRequest

    def test_submit(self):
        """ Test the submit method for a normal request.

        """
        self.request.location(sids=("okc", "tul"))
        self.request.metadata("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return


class StnDataRequestTest(_RequestTest):
    """ Unit testing for the StnDataRequest class.

    """
    _JSON_FILE = "data/StnData.json"
    _TEST_CLASS = StnDataRequest

    def test_submit(self):
        """ Test the submit method.

        """
        self.request.location(sid="okc")
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_element("mint", smry="min")
        self.request.add_element("maxt", smry="max")
        self.request.metadata("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return


class MultiStnDataRequestTest(_RequestTest):
    """ Unit testing for the MultiStnDataRequest class.

    """
    _JSON_FILE = "data/MultiStnData.json"
    _TEST_CLASS = MultiStnDataRequest

    def test_single_date(self):
        """ Test for a single date.
        
        Added due to a bug, so don't refactor it away!
        """
        self.request.dates("2011-12-31")
        self.assertTrue(True)  # pass if no exception
        return
            
    def test_submit(self):
        """ Test the submit method.

        """
        self.request.location(sids=("okc", "tul"))
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_element("mint", smry="min")
        self.request.add_element("maxt", smry="max")
        self.request.metadata("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (StnMetaRequestTest, StnDataRequestTest, MultiStnDataRequestTest)

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
