""" Testing for the the result.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unit

import unittest

from _data import TestData

from acis import ResultError
from acis import StnMetaResult
from acis import StnDataResult
from acis import MultiStnDataResult


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class StnMetaResultTest(unittest.TestCase):
    """ Unit testing for the StnMetaResult class.

    """
    _class = StnMetaResult
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the StnMetaResultTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/StnMeta.xml")
        return    
   
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        params = self._DATA.params
        result = self._DATA.result
        self._query = {"params": params, "result": result}
        self._meta = StnMetaResultTest._DATA.meta
        return

    def test_meta(self):
        """ Test the meta attribute.

        Metadata should be stored grouped by site and stored as a dict keyed
        to the site UID.

        """
        result = self._class(self._query)
        self.assertDictEqual(self._meta, result.meta)
        return

    def test_uid_missing(self):
        """ Test for exception for missing site UID.

        """
        self._query["result"]["meta"][0].pop("uid")
        self.assertRaises(ResultError, self._class, self._query)
        return

        
class _DataResultTest(StnMetaResultTest):
    """ Private base class for testing result classes with data.

    All results with data are expected to share the same interface for that
    data. This class should be excluded from test discovery and execution.

    """
    _class = None  # the class under test
    
    @classmethod
    def setUpClass(cls):
        raise NotImplementedError
            
    def test_uid_missing(self):
        """ Test for exception for missing site UID.

        """
        raise NotImplementedError
                
    def test_data(self):
        """ Test the data attribute.

        """
        result = self._class(self._query)
        self.assertDictEqual(self._data, result.data)
        return

    def test_smry(self):
        """ Test the smry attribute.

        """
        result = self._class(self._query)
        self.assertDictEqual(self._smry, result.smry)
        return

    def test_elems(self):
        """ Test the elems attribute.

        """
        result = self._class(self._query)
        self.assertSequenceEqual(self._elems, result.elems)
        return

    def test_len(self):
        """ Test the __len__ method.

        """
        result = self._class(self._query)
        self.assertEqual(len(self._records), len(result))
        return

    def test_iter(self):
        """ Test the __iter__ method.

        """
        # Iteration is tested twice to check for idempotentcy.
        result = self._class(self._query)
        self.assertSequenceEqual(self._records, list(result))
        self.assertSequenceEqual(self._records, list(result))
        return

         
class StnDataResultTest(_DataResultTest):
    """ Unit testing for the StnDataResult class.

    """
    _class = StnDataResult
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the StnDataResultTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/StnData.xml")
        return  
          
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        params = self._DATA.params
        result = self._DATA.result
        self._query = {"params": params, "result": result}
        self._meta = self._DATA.meta
        self._data = self._DATA.data
        self._smry = self._DATA.smry
        self._records = self._DATA.records
        self._elems = self._DATA.elems
        return

    def test_uid_missing(self):
        """ Test for exception for missing site UID.
        
        """
        self._query["result"]["meta"].pop("uid")
        self.assertRaises(ResultError, self._class, self._query)
        return

    def test_smry_only(self):
        """ Test a smry_only result.

        """
        del self._query["result"]["data"]
        result = self._class(self._query)
        self.assertDictEqual(self._smry, result.smry)
        for record in result:  
            self.assertTrue(False)  # data should be empty
        return


class MultiStnDataResultTest(_DataResultTest):
    """ Unit testing for the MultiStnDataResultTest class.

    """
    _class = MultiStnDataResult
    
    @classmethod
    def setUpClass(cls):
        """ Initialize the StnMetaResult class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/MultiStnData.xml")
        return  
          
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        params = self._DATA.params
        result = self._DATA.result
        self._query = {"params": params, "result": result}
        self._meta = self._DATA.meta
        self._data = self._DATA.data
        self._smry = self._DATA.smry
        self._records = self._DATA.records
        self._elems = self._DATA.elems
        return

    def test_uid_missing(self):
        """ Test for exception for missing site UID.
        
        """
        self._query["result"]["data"][0]["meta"].pop("uid")
        self.assertRaises(ResultError, self._class, self._query)
        return

    def test_smry_only(self):
        """ Test a smry_only result.

        """
        for site in self._query["result"]["data"]:    
            del site["data"]
        result = self._class(self._query)
        self.assertDictEqual(self._smry, result.smry)
        for record in result:  
            self.assertTrue(False)  # data should be empty
        return


# Specify the test cases to run for this module. Abstract bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (StnMetaResultTest, StnDataResultTest, MultiStnDataResultTest)

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
