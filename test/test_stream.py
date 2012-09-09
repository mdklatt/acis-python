""" Testing for the the stream.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import json
import sys
import unittest

import env
from acis import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TestStream(unittest.TestCase):
    """ Private base class for testing stream classes.

    """
    JSON_FILE = None
    STREAM_CLASS = None

    @classmethod
    def load_json(cls):
        """ Load the JSON test data.

        """
        return json.load(open(cls.JSON_FILE, "r"))

    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        test_data = self.load_json()
        self.meta = test_data["meta"]
        self.records = test_data["records"]
        self.stream = self.STREAM_CLASS()
        return


class TestStnDataStream(_TestStream):
    """ Unit testing for the StnDataStream class.

    """
    JSON_FILE = "data/StnDataCsv.json"
    STREAM_CLASS = StnDataStream

    def test_iter(self):
        self.stream.dates("2011-12-31", "2012-01-01")
        self.stream.location(sid="okc")
        self.stream.add_elem("mint")
        self.stream.add_elem("maxt")
        fields = ["sid", "date"] + self.stream.fields
        for i, record in enumerate(self.stream):
            self.assertSequenceEqual(record.values(), self.records[i])
            self.assertSequenceEqual(record.keys(), fields)
        self.assertEqual(i + 1, 2)
        self.assertDictEqual(self.stream.meta, self.meta)
        return


class TestMultiStnDataStream(_TestStream):
    """ Unit testing for the MultiStnDataStream class.

    """
    JSON_FILE = "data/MultiStnDataCsv.json"
    STREAM_CLASS = MultiStnDataStream

    def test_iter(self):
        self.stream.date("2011-12-31")
        self.stream.location(sids="okc,tul")
        self.stream.add_elem("mint")
        self.stream.add_elem("maxt")
        fields = ["sid", "date"] + self.stream.fields
        for i, record in enumerate(self.stream):
            self.assertSequenceEqual(record.values(), self.records[i])
            self.assertSequenceEqual(record.keys(), fields)
        self.assertEqual(i + 1, 2)
        self.assertDictEqual(self.stream.meta, self.meta)
        return



# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

TEST_CASES = (TestStnDataStream, TestMultiStnDataStream)

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

