""" Testing for the the util.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import unittest

import _env

from acis import sids_types


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.


class SidsTypesFunctionTest(unittest.TestCase):
    """ Unit testing for the sids_types function.

    """
    def test(self):
        """ Test normal operation.

        """
        sids = ("13967 1", "346661 2")
        types = {"WBAN": "13967", "COOP": "346661"}
        self.assertDictEqual(sids_types(sids), types)
        return

    def test_bad_format(self):
        """ Test exception for invalid sid format.

        """
        sids = ("13967",)  # no type code
        with self.assertRaises(ValueError) as context:
            sids_types(sids)
        message = "invalid sid: 13967"
        self.assertEqual(context.exception.message, message)
        return

    def test_unknown_type(self):
        """ Test exception for unknown type code.

        """
        sids = ("13967 9999",)
        with self.assertRaises(ValueError) as context:
            sids_types(sids)
        message = "unknown sid type: 9999"
        self.assertEqual(context.exception.message, message)
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (SidsTypesFunctionTest,)

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
