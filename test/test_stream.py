""" Testing for the the stream.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import json
import unittest

import _env
from acis.stream import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _StreamTest(unittest.TestCase):
    """ Private base class for testing stream classes.

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
        self.meta = test_data["meta"]
        self.records = test_data["records"]
        self.stream = self._TEST_CLASS()
        return


class StnDataStreamTest(_StreamTest):
    """ Unit testing for the StnDataStream class.

    """
    _JSON_FILE = "data/StnDataCsv.json"
    _TEST_CLASS = StnDataStream

    def test_iter(self):
        """ Test the __iter__ method.

        """
        self.stream.dates("2011-12-31", "2012-01-01")
        self.stream.location(sid="okc")
        self.stream.add_element("mint")
        self.stream.add_element("maxt")
        elems = ["sid", "date"] + list(self.stream.elems)
        self.assertSequenceEqual(list(self.stream), self.records)
        self.assertDictEqual(self.stream.meta, self.meta)
        return


class MultiStnDataStreamTest(_StreamTest):
    """ Unit testing for the MultiStnDataStream class.

    """
    _JSON_FILE = "data/MultiStnDataCsv.json"
    _TEST_CLASS = MultiStnDataStream

    def test_iter(self):
        """ Test the __iter__ method.

        """
        self.stream.date("2011-12-31")
        self.stream.location(sids="okc,tul")
        self.stream.add_element("mint")
        self.stream.add_element("maxt")
        elems = ["sid", "date"] + list(self.stream.elems)
        self.assertSequenceEqual(list(self.stream), self.records)
        self.assertDictEqual(self.stream.meta, self.meta)
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (StnDataStreamTest, MultiStnDataStreamTest)

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

