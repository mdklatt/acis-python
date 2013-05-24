""" Testing for the the util.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest
from _data import TestData

from acis import result_array
from acis import decode_sids
from acis import StnDataResult


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class DecodeSidsFunctionTest(unittest.TestCase):
    """ Unit testing for the decode_sids function.

    """
    def test(self):
        """ Test normal operation.

        """
        sids = ("13967 1", "346661 2", "346664 2")
        table = {"WBAN": ["13967"], "COOP": ["346661", "346664"]}
        self.assertDictEqual(table, decode_sids(sids))
        return

    def test_unknown_type(self):
        """ Test for unknown network type.

        """
        sids = ("13967 9999",)
        self.assertEqual(9999, decode_sids(sids).keys()[0])
        return

    def test_bad_format(self):
        """ Test exception for invalid sid format.

        """
        sids = ("13967",)  # missing type code
        with self.assertRaises(ValueError) as context:
            decode_sids(sids)
        message = "invalid SID: 13967"
        self.assertEqual(message, str(context.exception))
        return


class ResultArrayFunctionTest(unittest.TestCase):
    """ Unit testing for the result_array function.
    
    """
    @classmethod
    def setUpClass(cls):
        """ Initialize the ResultArrayFunctionTest class.
        
        This is called before any tests are run. This is part of the unittest
        API.
        
        """
        cls._DATA = TestData("data/StnData.xml")
        return  

    def test(self):
        """ Test normal operation.
        
        """
        query = {"params": self._DATA.params, "result": self._DATA.result}
        result = StnDataResult(query)
        array = result_array(result)
        for expected, actual in zip(result, array):
            self.assertSequenceEqual(expected, actual)
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (DecodeSidsFunctionTest, ResultArrayFunctionTest)

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
