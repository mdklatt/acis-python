""" Testing for the the request.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import json
import sys
import unittest

import env
from acis import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TestRequest(unittest.TestCase):
    """ Private base class for testing request classes.

    """
    JSON_FILE = None
    REQUEST_TYPE = None

    @classmethod
    def load_json(cls):
        """ Load the JSON test data.

        """
        return json.load(open(cls.JSON_FILE, "r"))

    def setUp(self):
        test_data = self.load_json()
        params = test_data["params"]
        result = test_data["result"]
        self.query = {"params": params, "result": result}
        self.request = self.REQUEST_TYPE()
        return


class TestStnMetaRequest(_TestRequest):
    """ Unit testing for the StnMetaRequest class.

    """
    JSON_FILE = "data/StnMeta.json"
    REQUEST_TYPE = StnMetaRequest

    def test_submit(self):
        """ Test the 'submit()' method.

        The function should return the parameters submitted to and the decoded
        object received from the server as a dict.

        """
        self.request.location(sids=("okc", "tul"))
        self.request.meta("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return



class TestStnDataRequest(_TestRequest):
    """ Unit testing for the StnDataRequest class.

    """
    JSON_FILE = "data/StnData.json"
    REQUEST_TYPE = StnDataRequest

    def test_submit(self):
        """ Test the 'submit()' method.

        The function should return the parameters submitted to and the decoded
        object received from the server.

        """
        self.request.location(sid="okc")
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_elem("mint", smry="min")
        self.request.add_elem("maxt", smry="max")
        self.request.meta("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return


class TestMultiStnDataRequest(_TestRequest):
    """ Unit testing for the MultiStnDataRequest class.

    """
    JSON_FILE = "data/MultiStnData.json"
    REQUEST_TYPE = MultiStnDataRequest

    #@unittest.skip("skip for debugging")
    def test_submit(self):
        """ Test the 'submit()' method.

        The function should return the parameters submitted to and the decoded
        object received from the server.

        """
        self.request.location(sids=("okc", "tul"))
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_elem("mint", smry="min")
        self.request.add_elem("maxt", smry="max")
        self.request.meta("county", "name")  # uid should be automatic
        query = self.request.submit()
        self.assertDictEqual(query["result"], self.query["result"])
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

TEST_CASES = (TestStnMetaRequest, TestStnDataRequest, TestMultiStnDataRequest)

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
    unittest.main()  # main() calls sys.exit()
