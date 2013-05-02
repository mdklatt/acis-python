""" Testing for the the stream.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest
from _data import TestData

from acis.stream import StnDataStream
from acis.stream import MultiStnDataStream


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _StreamTest(unittest.TestCase):
    """ Private base class for testing stream classes.

    This class should be excluded from test discovery and execution. Child
    classes must define the _DATA and _class class attributes.

    """
    @classmethod
    def setUpClass(cls):
        raise NotImplementedError

    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """    
        self._meta = self._DATA.meta
        self._records = self._DATA.records
        self._stream = self._class()
        return

    def test_elems(self):
        """ Test the add_element method and related functionality.
        
        """
        self.assertSequenceEqual([], self._stream.elems)
        self._stream.add_element("maxt")
        self._stream.add_element(2)
        self.assertSequenceEqual(("maxt", "vx2"), self._stream.elems)
        self._stream.add_element("maxt")  # duplicates ok
        self.assertSequenceEqual(("maxt_0", "vx2", "maxt_1"), 
                                                            self._stream.elems)
        self._stream.clear_elements()
        self.assertSequenceEqual([], self._stream.elems)        
        return

    def test_interval(self):
        """ Test the interval method.
        
        """
        self._stream.interval("dly")
        self._stream.interval("mly")
        self._stream.interval("yly")
        self._stream.interval((0, 1, 0))
        self._stream.interval([1, 0, 0])
        self.assertTrue(True)  # no execptions
        return

class StnDataStreamTest(_StreamTest):
    """ Unit testing for the StnDataStream class.

    """
    _class = StnDataStream
    
    @classmethod
    def setUpClass(cls):
        cls._DATA = TestData("data/StnDataCsv.xml")
        return
        
    def test_iter(self):
        """ Test the __iter__ method.

        """
        self._stream.dates("2011-12-31", "2012-01-01")
        self._stream.location(sid="okc")
        self._stream.add_element("mint")
        self._stream.add_element(1)  # maxt
        self.assertSequenceEqual(self._records, list(self._stream))
        self.assertDictEqual(self._meta, self._stream.meta)
        return


class MultiStnDataStreamTest(_StreamTest):
    """ Unit testing for the MultiStnDataStream class.

    """
    _class = MultiStnDataStream
    
    @classmethod
    def setUpClass(cls):
        cls._DATA = TestData("data/MultiStnDataCsv.xml")
        return

    def test_iter(self):
        """ Test the __iter__ method.

        """
        self._stream.date("2011-12-31")
        self._stream.location(sids="okc,OKCthr")
        self._stream.add_element("mint")
        self._stream.add_element(1)  # maxt
        self.assertSequenceEqual(self._records, list(self._stream))
        self.assertDictEqual(self._meta, self._stream.meta)
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

