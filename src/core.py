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
import numpy
import dateutil.relativedelta as relativedelta

	
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


def date_delta(interval):
	deltas = {
		'dly': datetime.timedelta(days=1),
		'mly': relativedelta.relativedelta(months=1),
		'yly': relativedelta.relativedelta(years=1),
	}
	try:
		delta = deltas[interval]
	except KeyError:
		raise ValueError('unknown interval')
	return delta
	
	
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
	_server = 'http://data.rcc-acis.org'
	
	def __init__(self, action, server='http://data.rcc-acis.org'):
		self.url = urlparse.urljoin(Request._server, action)
		self.params = None
		return
		
	def get(self, params):
		"""
		Request the data defined by 'params' from the server.
		
		The request is returned as an ACIS result JSON object.
		"""
		HTTP_OK = 200; HTTP_NF = 404
		self.params = json.dumps(params)
		query = urllib.urlencode({ 'params': self.params })
		conn = urllib.urlopen(self.url, data=query)  # POST request
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
		
		Elements must be specified using the full object syntax, i.e.
		{ 'name': 'elem', ... }. Sites are keyed by their ACIS UID, so this
		must be included in the 'meta' parameter, i.e. 'meta': 'uid'.
		"""
		result = Request.get(self, params)
		self.meta = { site.pop('uid'): site for site in result['meta'] }
 		return

		
class StnDataRequest(Request):
	"""
	A single-station data request.
	
	"""
	def __init__(self, params=None):
		Request.__init__(self, 'StnData')
		if params is not None:
			self.get(params)
		return

	def get(self, params):
		"""
		Retrieve and parse a StnData request.
		
		Elements must be specified using the full object syntax, i.e.
		{ 'name': 'elem', ... }. Sites are keyed by their ACIS UID, so this
		must be included in the 'meta' parameter, i.e. 'meta': 'uid'.
		"""
		elems = ( elem['name'] for elem in params['elems'] )
 		dtype = [('uid', int), ('date', object)] + [(elem, object) for elem 
 			in elems]	
		result = Request.get(self, params)
		uid = result['meta'].pop('uid')
		self.meta = { uid: result['meta'] }
		data = []
		for record in result['data']:
			date = parse_date(record[0])
			data.append(tuple([uid, date] + record[1:]))
		self.data = numpy.array(data, dtype)
		return

				
class MultiStnDataRequest(Request):

	def __init__(self, params=None):
		Request.__init__(self, 'MultiStnData')
		if params is not None:
			self.get(params)
		return
		
	def get(self, params):
		"""
		Retrieve and parse a MultiStnData result.
		
		Elements must be specified using the full object syntax, i.e.
		{ 'name': 'elem', ... }. Sites are keyed by their ACIS UID, so this
		must be included in the 'meta' parameter. Requests with a groupby
		value are not currently supported.
		"""
		elems = ( elem['name'] for elem in params['elems'] )
 		dtype = [('uid', int), ('date', object)] + [(elem, object) for elem 
 			in elems]	
		if 'date' in params:
			sdate = data_parse(params['date'])
		elif 'sdate' and 'edate' in params:
			sdate = parse_date(params['sdate'])
		delta = date_delta(params['elems'][0].get('interval', 'dly'))			
		result = Request.get(self, params)		
		self.meta = {}
		data = []
		for site in result['data']:
			date = sdate
			uid = site['meta'].pop('uid')
			self.meta[uid] = site['meta']
			for record in site['data']:
				data.append(tuple([uid, date] + record))
				date += delta
		self.data = numpy.array(data, dtype)
		return