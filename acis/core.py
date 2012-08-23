"""
Implementation of core ACIS classes.

"""
__version__ = '0.1.dev'
__all__ = ('ServerError', 'RequestError', 'Request', 'StnMetaRequest',
	'StnDataRequest', 'MultiStnDataRequest')

import datetime
import json
import re
import urllib
import urlparse
import dateutil.relativedelta as relativedelta


def date_delta(interval):
	deltas = {
		'dly': datetime.timedelta(days=1),
		'mly': relativedelta.relativedelta(months=1),
		'yly': relativedelta.relativedelta(years=1),
	}
	try:
		return deltas[interval]
	except KeyError:
		raise ValueError('uknown interval %s' % interval)
	
def parse_date(sdate):
	"""
	Parse a date string into a datetime.date object.
	
	Valid date formats are YYYY[-MM[-DD]] and hyphens are optional.
	"""
	date_regex = re.compile(r'^(\d{4})(?:-?(\d{2}))?(?:-?(\d{2}))?$')
	match = date_regex.search(sdate)
	try:
		y, m, d = (int(s) if s is not None else 1 for s in match.groups())
	except AttributeError:  # match is None
		raise ValueError('invalid date format')
	return datetime.date(y, m, d)
	
	
class ServerError(Exception):
	"""
	The server was unable to return a result object.
	
	This is reported as an HTTP status other than OK. In addition to the usual
	HTTP errors, this will occur if the server could not parse the request. The
	'status' attribute contains the HTTP status code.
	"""
	def __init__(self, message, status):
		Exception.__init__(self, status)
		self.status = status
		return
		

class RequestError(Exception):
	"""
	The returned result object is reporting an error.
	
	This is reported as an 'error' attribute in the result object. The server
	was able to parse the request, but it was invalid in some way.
	"""
	pass
		

class Request(object):
	"""
	An ACIS request.
	
	"""	
	def __init__(self, action, server='http://data.rcc-acis.org'):
		self.server = urlparse.urljoin(server, action)
		
	def get(self, params):
		"""
		Request the data defined by 'params' from the server.
		
		The request is returned as an ACIS result JSON object.
		"""
		HTTP_OK = 200; HTTP_NF = 404
		self.params = params
		query = urllib.urlencode({ 'params': json.dumps(self.params) })
		conn = urllib.urlopen(self.server, data=query)  # POST request
		status = conn.getcode()
		if status != HTTP_OK:  # server did return a result object
			if status == HTTP_NF:  # server returns HTML not plain text
				message = 'resource not found'
			else:
				message = conn.read()  # server should return plain text
			raise ServerError(message, status)
		result = json.loads(conn.read())
		if 'error' in result:
			raise RequestError(result['error'])
		return result	

		
class StnMetaRequest(Request):

	def __init__(self, params=None):
		Request.__init__(self, 'StnMeta')
		if params is not None:
			self.get(params)
		return
		
	def get(self, params):
		"""
		Retrieve and parse a StnMeta request.
		
		"""
		result = Request.get(self, params)
		try:
			self.meta = { site.pop('uid'): site for site in result['meta'] }
		except KeyError:
			raise ValueError('uid is a required meta element')
		return
		

class DataRequest(Request):
	
	def __init__(self, action, params=None):
		Request.__init__(self, action)
		if params is not None:
			self.get(params)
		return
		
	def __len__(self):
		count = 0
		for uid in self.data:
			count += len(self.data[uid])
		return count
				
				
class StnDataRequest(DataRequest):
	"""
	A single-station data request.
	
	"""
	def __init__(self, params=None):
		DataRequest.__init__(self, 'StnData', params)
		return
		
	def get(self, params):
		"""
		Retrieve and parse a StnData request.
		
		"""
		result = Request.get(self, params)
		try:
			uid = result['meta'].pop('uid')
		except KeyError:
			raise ValueError('uid is a required meta element')
		self.meta = { uid: result['meta'] }
		self.data = { uid: result['data'] }
		return
		
	def __iter__(self):
	
		for uid, data in self.data.items():
			for record in data:
				record[0] = parse_date(record[0])
				record.insert(0, uid)
				yield tuple(record)
		return
		
						
class MultiStnDataRequest(DataRequest):

	def __init__(self, params=None):
		DataRequest.__init__(self, 'MultiStnData', params)
		
	def get(self, params):
		"""
		Retrieve and parse a MultiStnData result.
		
		"""
		result = DataRequest.get(self, params)
		self.meta = {}
		self.data = {}
		for site in result['data']:
			try:
				uid = site['meta'].pop('uid')
			except KeyError:
				raise ValueError('uid is a required meta element')
			self.meta[uid] = site['meta']
			self.data[uid] = site['data']
		return
		
	def __iter__(self):
		if 'date' in self.params:
			sdate = data_parse(self.params['date'])
		elif 'sdate' and 'edate' in self.params:
			sdate = parse_date(self.params['sdate'])
		try:
			interval = self.params['elems'][0]['interval']
		except (TypeError, KeyError):
			interval = 'dly'
		delta = date_delta(interval)
		for uid, data in self.data.items():
			date = sdate
			for record in data:
				record.insert(0, uid)
				record.insert(1, date)
				yield tuple(record)
				date += delta
		return