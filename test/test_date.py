""" Testing for the the date.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import datetime
import unittest

import _env
from _data import TestData

from acis import date_object
from acis import date_range
from acis import date_string


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.


class DateObjectFunctionTest(unittest.TestCase):
    """ Unit testing for the date_object function.

    """
    def test_day_hyphen(self):
        """ Test a YYYY-MM-DD string.

        """
        date_str = "2011-12-31"
        date_obj = datetime.date(2011, 12, 31)
        self.assertEqual(date_obj, date_object(date_str))
        return

    def test_day_no_hyphen(self):
        """ Test a YYYYMMDD string.

        """
        date_str = "20111231"
        date_obj = datetime.date(2011, 12, 31)
        self.assertEqual(date_obj, date_object(date_str))
        return

    def test_month_hyphen(self):
        """ Test a YYYY-MM string.

        """
        date_str = "2011-12"
        date_obj = datetime.date(2011, 12, 1)
        self.assertEqual(date_obj, date_object(date_str))
        return

    def test_month_no_hyphen(self):
        """ Test a YYYYMM string.

        """
        date_str = "201112"
        date_obj = datetime.date(2011, 12, 1)
        self.assertEqual(date_obj, date_object(date_str))
        return

    def test_year(self):
        """ Test a YYYY string.

        """
        date_str = "2011"
        date_obj = datetime.date(2011, 1, 1)
        self.assertEqual(date_obj, date_object(date_str))
        return

    def test_bad_year(self):
        """ Test exception for a two-digit year.

        """
        date_str = "11-11-11"
        self.assertRaises(ValueError, date_object, date_str)
        return


class DateStringFunctionTest(unittest.TestCase):
    """ Unit testing for the date_object function.

    """
    def test_normal(self):
        """ Test normal operation.

        """
        date_obj = datetime.date(2012, 1, 1)
        date_str = "2012-01-01"  # test for zero fill
        self.assertEqual(date_str, date_string(date_obj))
        return

    def test_bad_arg(self):
        """ Test exception for invalid argument type.

        """
        with self.assertRaises(TypeError) as context:
            date_string(None)
        message = "need a date object"
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
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_daily_str(self):
        """ Test daily interval "dly".

        """
        params = {"sdate": "2011-12-31", "edate": "2012-01-01",
                "elems": [{"name": "mint", "interval": "dly"}]}
        dates = ("2011-12-31", "2012-01-01")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_daily_ymd(self):
        """ Test daily interval [0, 0, 2]

        """
        params = {"sdate": "2011-12-31", "edate": "2012-01-05",
                "elems": [{"name": "mint", "interval": [0, 0, 2]}]}
        dates = ("2011-12-31", "2012-01-02", "2012-01-04")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_monthly_str(self):
        """ Test a monthly interval "mly".

        """
        params = {"sdate": "2011-12-01", "edate": "2012-01-01",
                "elems": [{"name": "mint", "interval": "mly"}]}
        dates = ("2011-12-01", "2012-01-01")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_monthly_ymd(self):
        """ Test monthly interval [0, 2, 0]

        """
        params = {"sdate": "2011-12-01", "edate": "2012-05-01",
                  "elems": [{"name": "mint", "interval": [0, 2, 0]}]}
        dates = ("2011-12-01", "2012-02-01", "2012-04-01")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_yearly_str(self):
        """ Test yearly interval "yly".

        """
        params = {"sdate": "2011-01-01", "edate": "2012-01-01",
                  "elems": [{"name": "mint", "interval": "yly"}]}
        dates = ("2011-01-01", "2012-01-01")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    def test_yearly_ymd(self):
        """ Test yearly interval [2, 0, 0].

        """
        params = {"sdate": "2011-01-01", "edate": "2016-01-01",
                  "elems": [{"name": "mint", "interval": (2,0,0)}]}
        dates = ("2011-01-01", "2013-01-01", "2015-01-01")
        self.assertSequenceEqual(dates, list(date_range(params)))
        return

    # This fails due to a less restrictive date_range() funtion. Intervals
    # are normalized for Requests and Streams; is it necessary to normalize for
    # manually created params objects?
    @unittest.expectedFailure  
    def test_ymd_mutex(self):
        """ Test that y, m, d specifications are mutually exclusive.

        The least significant place takes precedence. 
        
        """
        params = {"sdate": "2011-01-01", "edate": "2011-02-02",
                  "elems": [{"interval": (0, 1, 1)}]}
        dates = ("2011-01-01", "2011-01-02")
        self.assertSequenceEqual(dates, list(date_range(params))[:2])
        params = {"sdate": "2011-01-01", "edate": "2012-02-01",
                  "elems": [{"interval": (1, 1, 0)}]}
        dates = ("2011-01-01", "2011-02-01")
        self.assertSequenceEqual(dates, list(date_range(params))[:2])
        params = {"sdate": "2011-01-01", "edate": "2012-01-02",
                  "elems": [{"interval": (1, 0, 1)}]}
        dates = ("2011-01-01", "2011-01-02")
        self.assertSequenceEqual(dates, list(date_range(params))[:2])
        return

    def test_bad_params(self):
        """ Test exception for invalid date range specification.

        """
        params = {"sdate": "2013-01-01", "elems": "mint"}  # no edate
        with self.assertRaises(ValueError) as context:
            list(date_range(params))  # list needed to trigger iteration
        message = "invalid date range specification"
        self.assertEqual(context.exception.message, message)
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
