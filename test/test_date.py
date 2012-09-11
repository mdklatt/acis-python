""" Testing for the the date.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import datetime
import unittest

import _env
from acis.date import *


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.


class DateObjectFunctionTest(unittest.TestCase):
    """ Unit testing for the date_object function.

    """
    def test_day_hyphen(self):
        """ Test a YYYY-MM-DD string.

        """
        string = "2011-12-31"
        object = datetime.date(2011, 12, 31)
        self.assertEquals(date_object(string), object)
        return

    def test_day_no_hyphen(self):
        """ Test a YYYYMMDD string.

        """
        string = "20111231"
        object = datetime.date(2011, 12, 31)
        self.assertEquals(date_object(string), object)
        return

    def test_month_hyphen(self):
        """ Test a YYYY-MM string.

        """
        string = "2011-12"
        object = datetime.date(2011, 12, 1)
        self.assertEquals(date_object(string), object)
        return

    def test_month_no_hyphen(self):
        """ Test a YYYYMM string.

        """
        string = "201112"
        object = datetime.date(2011, 12, 1)
        self.assertEquals(date_object(string), object)
        return

    def test_year(self):
        """ Test a YYYY string.

        """
        string = "2011"
        object = datetime.date(2011, 1, 1)
        self.assertEquals(date_object(string), object)
        return

    def test_bad_year(self):
        """ Test for an error with a two-digit year.

        """
        string = "11-11-11"
        self.assertRaises(ValueError, date_object, string)
        return


class DateStringFunctionTest(unittest.TestCase):
    """ Unit testing for the date_object function.

    """
    def test(self):
        """ Test a date object.

        """
        object = datetime.date(2012, 1, 1)
        string = "2012-01-01"  # zero fill
        self.assertEquals(date_string(object), string)
        return


class DateRangeFunctionTest(unittest.TestCase):
    """ Unit testing for the date_range function.

    """
    def test_default(self):
        """ Test a daily default interval.

        """
        params = {"sdate": "2011-12-31", "edate": "2012-01-01",
            "elems": "mint"}  # no interval given
        dates = ("2011-12-31", "2012-01-01")
        self.assertSequenceEqual(list(date_range(params)), dates)
        return

    def test_daily(self):
        """ Test a daily ("dly") interval.

        """
        params = {"sdate": "2011-12-31", "edate": "2012-01-01",
                "elems": [{"name": "mint", "interval": "dly"}]}
        dates = ("2011-12-31", "2012-01-01")
        self.assertSequenceEqual(list(date_range(params)), dates)
        return

    def test_monthly(self):
        """ Test a monthly ("mly") interval.

        """
        params = {"sdate": "2011-12-01", "edate": "2012-01-01",
                "elems": [{"name": "mint", "interval": "mly"}]}
        dates = ("2011-12-01", "2012-01-01")
        self.assertSequenceEqual(list(date_range(params)), dates)
        return

    def test_yearly(self):
        """ Test a yearly ("yly") interval.

        """
        params = {"sdate": "2011-01-01", "edate": "2012-01-01",
                "elems": [{"name": "mint", "interval": "yly"}]}
        dates = ("2011-01-01", "2012-01-01")
        self.assertSequenceEqual(list(date_range(params)), dates)
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (DateObjectFunctionTest, DateStringFunctionTest,
        DateRangeFunctionTest)

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
