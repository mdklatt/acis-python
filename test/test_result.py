""" Testing for the the result.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import datetime
import json
import sys
import unittest

import env
from acis import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TestResult(unittest.TestCase):
    """ Private base class for testing result classes.

    This class should be excluded from test discovery and execution. Child
    classes must define JSON_FILE and RESULT_CLASS class attributes

    """
    JSON_FILE = None

    @classmethod
    def load_json(cls):
        """ Load the JSON test data.

        """
        return json.load(open(cls.JSON_FILE, "r"))


class _TestMetaResult(_TestResult):
    """ Private base class for testing result classes with metadata.

    All results with metadata are expected to share the same interface for that
    metadata. This class should be excluded from test discovery and execution.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        test_data = self.load_json()
        params = test_data["params"]
        result = test_data["result"]
        self.query = {"params": params, "result": result}
        self.meta = test_data["meta"]
        return

    def test_meta(self):
        """ Test the 'meta' attribute.

        Metadata should be stored grouped by site and stored as a dict keyed
        to the site UID.

        """
        result = self.RESULT_CLASS(self.query)
        for uid, site in result.meta.items():
            self.assertDictEqual(site, self.meta[str(uid)])
        return


class _TestDataResult(_TestResult):
    """ Private base class for testing result classes with data.

    All results with data are expected to share the same interface for that
    data. This class should be excluded from test discovery and execution.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        test_data = self.load_json()
        params = test_data["params"]
        result = test_data["result"]
        self.query = {"params": params, "result": result}
        self.fields = [elem["name"] for elem in params["elems"]]
        self.meta = test_data["meta"]
        self.data = test_data["data"]
        self.smry = test_data["smry"]
        self.records = test_data["records"]
        return

    def test_data(self):
        """ Test the 'data' attribute.

        Data should be grouped by site and stored as a dict keyed to the site
        UID.

        """
        result = self.RESULT_CLASS(self.query)
        for uid, data in result.data.items():
            self.assertSequenceEqual(data, self.data[str(uid)])
        return

    def test_smry(self):
        """ Test the 'smry' attribute.

        Summary records should be grouped by site and stored as a dict keyed to
        the site UID. Each summary record should be an OrderedDict containing
        the value of each element in the order specified in the request
        parameters.

        """
        result = self.RESULT_CLASS(self.query)
        for uid, smry in result.smry.items():
            self.assertSequenceEqual(smry.values(), self.smry[str(uid)])
            self.assertSequenceEqual(smry.keys(), self.fields)
        return

    def test_fields(self):
        """ Test the 'fields' attribute.

        This attribute should be a list of the element names, in order, in the
        request parameters.

        """
        result = self.RESULT_CLASS(self.query)
        self.assertSequenceEqual(result.fields, self.fields)
        return

    def test_len(self):
        """ Test the '__len__' method.

        The length of a result should be equal to the number of records to be
        iterated over.

        """
        result = self.RESULT_CLASS(self.query)
        self.assertEqual(len(result), len(self.records))
        return

    def test_iter(self):
        """ Test the '__iter__' method.

        Iterating over a result should produce each record in the 'data'
        attribute. The record should be an OrderedDict containing the the UID,
        the date, and the value of each element in the order specified in the
        request parameters.

        """
        result = self.RESULT_CLASS(self.query)
        fields = ["uid", "date"] + self.fields
        for i, record in enumerate(result):
            self.assertSequenceEqual(record.values(), self.records[i])
            self.assertSequenceEqual(record.keys(), fields)
        self.assertEqual(i + 1, len(result))
        return


class TestStnMetaResult(_TestMetaResult):
    """ Unit testing for the StnMetaResult class.

    """
    JSON_FILE = "data/StnMeta.json"
    RESULT_CLASS = StnMetaResult

    def test_no_uid(self):
        """ Test failure for missing 'uid'.

        """
        self.query["result"]["meta"][0].pop("uid")
        self.assertRaises(ParameterError, self.RESULT_CLASS, self.query)
        return


class TestStnDataResult(_TestDataResult, _TestMetaResult):
    """ Unit testing for the StnDataResult class.

    """
    JSON_FILE = "data/StnData.json"
    RESULT_CLASS = StnDataResult

    def test_no_uid(self):
        """ Test failure for missing 'uid'.

        """
        self.query["result"]["meta"].pop("uid")
        self.assertRaises(ParameterError, self.RESULT_CLASS, self.query)
        return


class TestMultiStnDataResult(_TestDataResult, _TestMetaResult):
    """ Unit testing for the MultiStnDataResult class.

    """
    JSON_FILE = "data/MultiStnData.json"
    RESULT_CLASS = MultiStnDataResult

    def test_no_uid(self):
        """ Test failure for missing 'uid'.

        """
        self.query["result"]["data"][0]["meta"].pop("uid")
        self.assertRaises(ParameterError, self.RESULT_CLASS, self.query)
        return



# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

TEST_CASES = (TestStnMetaResult, TestStnDataResult, TestMultiStnDataResult)

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
