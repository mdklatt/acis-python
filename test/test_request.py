""" Testing for the the request.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import json
import sys
import unittest
import urlparse

import localpath
from acis import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class TestRequest(unittest.TestCase):
    """ Unit testing for the Request class.

    """
    JSON_FILE = "StnData.json"
    REQUEST_TYPE = Request

    @classmethod
    def load_json(cls):
        """ Load the JSON test data.

        """
        return json.load(open(cls.JSON_FILE, "r"))

    def setUp(self):
        test_data = self.load_json()
        self.query = test_data["query"]
        self.params = test_data["params"]
        self.result = test_data["result"]
        self.request = self.REQUEST_TYPE(self.query)
        return

    def test_url(self):
        url = urlparse.urljoin(self.request.SERVER, self.query)
        self.assertEqual(self.request.url, url)
        return

    def test_submit(self):
        """ Test the 'submit()' method.

        When passed a dict of request parameters, the function should return
        the decoded result object from the server.

        """
        result = self.request.submit(self.params)
        self.assertDictEqual(result, self.result)
        return

    def test_request_error(self):
        """ Test the 'submit' method for an invalid request.

        A RequestError should be raised if an invalid request is submitted to
        the server.
        """
        self.params.pop("sid")
        self.assertRaises(RequestError, self.request.submit, self.params)
        return

    def test_result_error(self):
        """ The 'submit' method for an error result.

        A ResultError should be raised if the result object from the server
        has an error message.
        """
        self.params["sid"] = ""
        self.assertRaises(ResultError, self.request.submit, self.params)
        return


class _TestParamRequest(TestRequest):
    """ Private base class for testing advanced request classes.

    This class should be excluded from test discovery and execution. Child
    classes must define JSON_FILE and REQUEST_TYPE class attributes. The
    'test_request_error' and 'test_result_error' methods need to be overridden
    to produce the desired errors for the query type.

    """
    def setUp(self):
        test_data = self.load_json()
        self.query = test_data["query"]
        self.params = test_data["params"]
        self.result = test_data["result"]
        self.request = self.REQUEST_TYPE()
        return


class TestStnMetaRequest(_TestParamRequest):
    """ Unit testing for the StnMetaRequest class.

    """
    JSON_FILE = "StnMeta.json"
    REQUEST_TYPE = StnMetaRequest

    @unittest.expectedFailure  # until request and result are decoupled
    def test_submit(self):
        """ Test the 'submit()' method.

        When passed a dict of request parameters, the function should return
        the decoded result object from the server.

        """
        self.request.location(uid=("okc", "tul"))
        self.request.meta("county", "name")  # uid should be automatic
        result = self.request.submit()
        self.assertDictEqual(result, self.result)
        return

    def test_request_error(self):
        """ Test the 'submit' method for an invalid request.

        A RequestError should be raised if an invalid request is submitted to
        the server.

        """
        self.request.location(bbox="")
        self.assertRaises(RequestError, self.request.submit)
        return

    @unittest.expectedFailure  # how do you get an error result from StnMeta??
    def test_result_error(self):
        """ The 'submit' method for an error result.

        A ResultError should be raised if the result object from the server
        has an error message.

        """
        raise NotImplementedError
        return


class TestStnDataRequest(_TestParamRequest):
    """ Unit testing for the StnDataRequest class.

    """
    JSON_FILE = "StnData.json"
    REQUEST_TYPE = StnDataRequest

    @unittest.expectedFailure  # until request and result are decoupled
    def test_submit(self):
        """ Test the 'submit()' method.

        When passed a dict of request parameters, the function should return
        the decoded result object from the server.

        """
        self.request.location(sid="okc")
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_element("mint", smry="min")
        self.request.add_element("maxt", smry="max")
        self.request.meta("county", "name")  # uid should be automatic
        result = self.request.submit()
        self.assertDictEqual(result, self.result)
        return

    def test_request_error(self):
        """ Test the 'submit' method for an invalid request.

        A RequestError should be raised if an invalid request is submitted to
        the server.

        """
        self.assertRaises(RequestError, self.request.submit)  # empty params
        return

    def test_result_error(self):
        """ The 'submit' method for an error result.

        A ResultError should be raised if the result object from the server
        has an error message.

        """
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.location(sid="")
        self.assertRaises(ResultError, self.request.submit)
        return


class TestMultiStnDataRequest(_TestParamRequest):
    """ Unit testing for the MultiStnDataRequest class.

    """
    JSON_FILE = "MultiStnData.json"
    REQUEST_TYPE = MultiStnDataRequest

    @unittest.expectedFailure  # until request and result are decoupled
    def test_submit(self):
        """ Test the 'submit()' method.

        When passed a dict of request parameters, the function should return
        the decoded result object from the server.

        """
        self.request.location(sid="okc")
        self.request.dates("2011-12-31", "2012-01-01")
        self.request.add_element("mint", smry="min")
        self.request.add_element("maxt", smry="max")
        self.request.meta("county", "name")  # uid should be automatic
        result = self.request.submit()
        self.assertDictEqual(result, self.result)
        return

    def test_request_error(self):
        """ Test the 'submit' method for an invalid request.

        A RequestError should be raised if an invalid request is submitted to
        the server.

        """
        self.assertRaises(RequestError, self.request.submit)  # empty params
        return

    @unittest.expectedFailure
    def test_result_error(self):
        """ The 'submit' method for an error result.

        A ResultError should be raised if the result object from the server
        has an error message.

        """
        raise NotImplementedError


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

TEST_CASES = (TestRequest, TestStnMetaRequest, TestStnDataRequest,
    TestMultiStnDataRequest)

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
