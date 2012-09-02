import datetime
import sys
import unittest

import local
from acis import *

class RequestTest(unittest.TestCase):

    def setUp(self):
        self.request = Request("StnData")
        self.params = { "sid": "OKC", "elems": "maxt", "date": "20090101",
            "meta": "uid" }
        self.result = { "meta": { "uid": 92 }, "data": [["2009-01-01","57"]] }
        return

    def test_init(self):
        """ Test normal init. """
        url = "http://data.rcc-acis.org/StnData"
        self.assertEqual(self.request.url, url)
        return

    def test_submit(self):
        """ Test normal submit. """
        self.assertEqual(self.request.submit(self.params), self.result)
        return

    def test_submit_bad_request(self):
        """ Test submit failure. """
        self.params.pop("sid")
        self.assertRaises(RequestError, self.request.submit, self.params)
        return

    def test_submit_bad_request(self):
        """ Test submit failure. """
        self.params.pop("sid")
        self.assertRaises(RequestError, self.request.submit, self.params)
        return

    def test_submit_bad_result(self):
        """ Test submit failure. """
        self.params["sid"] = ""
        self.assertRaises(ResultError, self.request.submit, self.params)
        return


class StnMetaRequestTest(unittest.TestCase):

    def setUp(self):
        self.request = StnMetaRequest()
        return

    def test_url(self):
        url = "http://data.rcc-acis.org/StnMeta"
        self.assertEqual(self.request.url, url)
        return

    def test_default_meta(self):
        self.assertItemsEqual(self.request.params["meta"], ("uid",))
        return

    def test_meta(self):
        meta = ("uid", "county", "name")
        self.request.meta(*meta)
        self.assertItemsEqual(self.request.params["meta"], meta)
        return

    def test_location(self):
        location = {"sids": "OKC,TUL", "state": "OK"}
        self.request.location(**location)
        for key, value in location.items():
            self.assertEqual(self.request.params[key], value)
        return

class StnDataRequestTest(unittest.TestCase):

    def setUp(self):
        self.request = StnDataRequest()
        return

    def test_url(self):
        url = "http://data.rcc-acis.org/StnData"
        self.assertEqual(self.request.url, url)
        return

    def test_default_meta(self):
        self.assertItemsEqual(self.request.params["meta"], ("uid",))
        return

    def test_meta(self):
        meta = ("uid", "county", "name")
        self.request.meta(*meta)
        self.assertItemsEqual(self.request.params["meta"], meta)
        return

    def test_location_uid(self):
        uid = 92
        self.request.location(uid=uid)
        self.assertEqual(self.request.params["uid"], uid)
        return

    def test_location_sid(self):
        sid = "OKC"
        self.request.location(sid=sid)
        self.assertEqual(self.request.params["sid"], sid)
        return

    def test_location_none(self):
        self.assertRaises(ParameterError, self.request.location)
        return

    def test_dates_objects(self):
        sdate, edate = datetime.date(2009, 1, 1), datetime.date(2009, 1, 3)
        self.request.dates(sdate, edate)
        dates = [self.request.params[date] for date in ("sdate", "edate")]
        self.assertEqual(dates, ["20090101", "20090103"])
        return

    def test_dates_string(self):
        sdate, edate = "20090101", "20090103"
        self.request.dates(sdate, edate)
        dates = [self.request.params[date] for date in ("sdate", "edate")]
        self.assertEqual(dates, [sdate, edate])
        return

    def test_basic_elem(self):
        elems = [{"name": "maxt", "interval": "dly"}]
        self.request.add_element("maxt")
        self.assertEqual(self.request.params["elems"], elems)
        return

    def test_reduction_elem(self):
        name, interval, reduce = "maxt", "mly", "max"
        elems = [{"name": name, "interval": interval, "reduction": reduce}]
        self.request.add_element(name, interval=interval, reduction=reduce)
        self.assertEqual(self.request.params["elems"], elems)
        return


class MultiStnDataRequestTest(unittest.TestCase):

    def setUp(self):
        self.request = MultiStnDataRequest()
        return

    def test_url(self):
        url = "http://data.rcc-acis.org/MultiStnData"
        self.assertEqual(self.request.url, url)
        return

    def test_default_meta(self):
        self.assertItemsEqual(self.request.params["meta"], ("uid",))
        return

    def test_meta(self):
        meta = ("uid", "county", "name")
        self.request.meta(*meta)
        self.assertItemsEqual(self.request.params["meta"], meta)
        return

    def test_location(self):
        location = {"sids": "OKC,TUL", "state": "OK"}
        self.request.location(**location)
        for key, value in location.items():
            self.assertEqual(self.request.params[key], value)
        return

    def test_dates_objects(self):
        sdate, edate = datetime.date(2009, 1, 1), datetime.date(2009, 1, 3)
        self.request.dates(sdate, edate)
        dates = [self.request.params[date] for date in ("sdate", "edate")]
        self.assertEqual(dates, ["20090101", "20090103"])
        return

    def test_dates_string(self):
        sdate, edate = "20090101", "20090103"
        self.request.dates(sdate, edate)
        dates = [self.request.params[date] for date in ("sdate", "edate")]
        self.assertEqual(dates, [sdate, edate])
        return

    def test_basic_elem(self):
        elems = [{"name": "maxt", "interval": "dly"}]
        self.request.add_element("maxt")
        self.assertEqual(self.request.params["elems"], elems)
        return

    def test_reduction_elem(self):
        name, interval, reduce = "maxt", "mly", "max"
        elems = [{"name": name, "interval": interval, "reduction": reduce}]
        self.request.add_element(name, interval=interval, reduction=reduce)
        self.assertEqual(self.request.params["elems"], elems)
        return


if __name__ == "__main__":
    sys.exit(unittest.main())
