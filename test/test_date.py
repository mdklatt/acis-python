""" Testing for the the date.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import datetime

import _path
import _unittest as unittest
from _data import TestData


from acis import date_trunc
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


class DateTruncFunctionTest(unittest.TestCase):
    """ Unit testing for the date_trunc function.
    
    """
    def test_mly(self):
        """ Test "mly" interval.
        
        """
        self.assertEqual("2011-12", date_trunc("20111215", "mly"))
        self.assertEqual("2011-12", date_trunc("2011-12-05", "mly"))
        self.assertEqual("2011-12", date_trunc("2011-12", "mly"))
        self.assertEqual("2011-01", date_trunc("2011", "mly"))
        return

    def test_yly(self):
        """ Test "yly" interval".
        
        """
        self.assertEqual("2011", date_trunc("20111215", "yly"))
        self.assertEqual("2011", date_trunc("2011-12-05", "yly"))
        self.assertEqual("2011", date_trunc("2011-12", "yly"))
        self.assertEqual("2011", date_trunc("2011", "yly"))
        return

    def test_other(self):
        """ Test (yr, mo, da) sequences.
        
        """
        self.assertEqual("2011-12-15", date_trunc("2011-12-15", (0, 1, 0)))
        self.assertEqual("2011-12-15", date_trunc("2011-12-15", [1, 0, 0]))
        return
        

class DateRangeFunctionTest(unittest.TestCase):
    """ Unit testing for the date_range function.

    """
    def test_defaults(self):
        """ Test defaults for edate and interval.

        """
        expected = ("2011-12-31",)
        actual = date_range("2011-12-31")
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_daily_str(self):
        """ Test daily interval "dly".

        """
        expected = ("2011-12-31", "2012-01-01", "2012-01-02")
        actual = date_range("2011-12-31", "2012-01-02", "dly")
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_daily_ymd(self):
        """ Test daily interval (0, 0, 2)

        """
        expected = ("2011-12-31", "2012-01-02", "2012-01-04")
        actual = date_range("2011-12-31", "2012-01-04", (0, 0, 2))
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_monthly_str(self):
        """ Test a monthly interval "mly".

        """
        expected = ("2011-12", "2012-01", "2012-02")
        actual = date_range("20111215", "2012-02-15", "mly")
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_monthly_ymd(self):
        """ Test monthly interval (0, 2, 0)

        """
        expected = ("2011-12-15", "2012-02-15", "2012-04-15")
        actual = date_range("2011-12-15", "2012-04-15", (0, 2, 0))
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_yearly_str(self):
        """ Test yearly interval "yly".

        """
        expected = ("2011", "2012", "2013")
        actual = date_range("2011-12-15", "2013-12-15", "yly")
        self.assertSequenceEqual(expected, list(actual))
        return

    def test_yearly_ymd(self):
        """ Test yearly interval (2, 0, 0).

        """
        expected = ("2011-12-15", "2013-12-15", "2015-12-15")
        actual = date_range("2011-12-15", "2015-12-15", (2, 0, 0))
        self.assertSequenceEqual(expected, list(actual))
        return


# Specify the test cases to run for this module. Private bases classes need
# to be explicitly excluded from automatic discovery.

_TEST_CASES = (DateObjectFunctionTest, DateStringFunctionTest,
        DateTruncFunctionTest, DateRangeFunctionTest)

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
