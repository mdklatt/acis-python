""" Testing for the the request.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unit

import unittest

from _data import TestData

from acis import RequestError
from acis import StnMetaRequest
from acis import StnDataRequest
from acis import MultiStnDataRequest

# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _RequestTest(unittest.TestCase):
    """ Private base class for testing request classes.

    This class should be excluded from test discovery and execution. Child
    classes must define the _JSON_FILE and _TEST_CLASS class attributes.

    """
    @classmethod
    def setUpClass(cls):
        raise NotImplementedError
        
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        params = self._DATA.params
        result = self._DATA.result
        self._query = {"params": params, "result": result}
        self._request = self._class()
        return


class StnMetaRequestTest(_RequestTest):
    """ Unit testing for the StnMetaRequest class.

    """
    _class = StnMetaRequest
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the StnMetaRequestTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/StnMeta.xml")
        return
        
    def test_submit(self):
        """ Test the submit method for a normal request.

        """
        self._request.location(county="40109")
        self._request.dates("1890-01-01", "1907-11-15")
        self._request.elements(1, "mint")  # 1: maxt
        self._request.metadata("county", "name")  # uid should be automatic
        query = self._request.submit()
        self.assertDictEqual(self._query["result"], query["result"])
        return


class StnDataRequestTest(_RequestTest):
    """ Unit testing for the StnDataRequest class.

    """
    _class = StnDataRequest
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the StnDataRequestTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/StnData.xml")
        return

    def test_interval(self):
        """ Test the interval method.
        
        """
        self._request.interval("dly")
        self._request.interval("mly")
        self._request.interval("yly")
        self._request.interval((0, 1, 0))
        self._request.interval([1, 0, 0])
        self.assertTrue(True)  # no execptions
        return
        
    def test_submit(self):
        """ Test the submit method.

        """
        self._request.location(sid="okc")
        self._request.dates("2011-12-31", "2012-01-01")
        self._request.add_element("mint", smry="min")
        self._request.add_element(1, smry="max")  # select maxt by vX
        self._request.metadata("county", "name")  # uid should be automatic
        query = self._request.submit()
        self.assertDictEqual(self._query["result"], query["result"])
        return


class MultiStnDataRequestTest(_RequestTest):
    """ Unit testing for the MultiStnDataRequest class.

    """
    _class = MultiStnDataRequest
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the MultiStnDataRequestTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/MultiStnData.xml")
        return
        
    def test_single_date(self):
        """ Test for a single date.

        Added due to a bug, so don't refactor it away!
        """
        self._request.dates("2011-12-31")
        self.assertTrue(True)  # pass if no exception
        return

    def test_interval(self):
        """ Test the interval method.
        
        """
        self._request.interval("dly")
        self._request.interval("mly")
        self._request.interval("yly")
        self._request.interval((0, 1, 0))
        self._request.interval([1, 0, 0])
        self.assertTrue(True)  # no execptions
        return

    def test_submit(self):
        """ Test the submit method.

        """
        self._request.location(sids=("okc", "tul"))
        self._request.dates("2011-12-31", "2012-01-01")
        self._request.add_element("mint", smry="min")
        self._request.add_element("1", smry="max")  # select maxt by vX string
        self._request.metadata("county", "name")  # uid should be automatic
        query = self._request.submit()
        self.assertDictEqual(self._query["result"], query["result"])
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
