#!/usr/bin/python

from sys import stdout
import utillib.chron as chron
import acis

timer = chron.Timer()

print 'StnMetaRequest'
params = { 'climdiv': 'OK01', 'meta': ( 'uid', 'name' ) }
timer.start()
request = acis.StnMetaRequest(params)
timer.stop()
# print request.meta
print '%d records (%.3f seconds)' % (len(request.meta), timer.elapsed)


print 'StnDataRequest'
params = { 'sid': '340027', 'sdate': '20090101', 'edate': '20121231',
   'elems': [ {'name': 'maxt' },  { 'name': 'mint' } ], 
   'meta': ( 'uid', 'name' ) } 
timer.start()
request = acis.StnDataRequest(params)
timer.stop()
# for record in request:
# 	print record
# print request.meta
print '%d records (%.3f seconds)' % (len(request), timer.elapsed)


print 'StnDataRequest (large)'
elems = [{'name': elem} for elem in ('mint', 'maxt', 'obst', 'pcpn', 'snow',
 	'snwd')]
params = { 'sid': '344451', 'sdate': 'por', 'edate': 'por', 'elems': elems,
	'meta': ('uid', 'name') } 
timer.start()
request = acis.StnDataRequest(params)
timer.stop()
# for record in request:
# 	print record
# print request.meta
print '%d records (%.3f seconds)' % (len(request), timer.elapsed)


print 'MultStnDataRequest'
params = { 'sids': ('340017', '340027'), 'sdate': '20090101', 
	'edate': '20121231', 'elems': [ {'name': 'maxt' },  { 'name': 'mint' } ], 
	'meta': ( 'uid', 'name' ) }
timer.start() 
request = acis.MultiStnDataRequest(params)
timer.stop()
# for record in request:
#	print record
# print request.meta
print '%d records (%.3f seconds)' % (len(request), timer.elapsed)


print 'MultiStnDataRequest (reductions)'
maxt = { 'name': 'maxt', 'interval': 'mly', 'duration': 'mly',
	'reduce': { 'reduce': 'min', 'add': 'date' } }
pcpn = {'name': 'pcpn', 'interval': 'mly', 'duration': 'ytd', 
	'reduce': { 'reduce': 'sum', 'add': 'mcnt' } }
params = { 'sids': ( '340017', '340027' ), 'meta': ( 'uid', 'name' ), 
	'elems': ( maxt, pcpn ), 'sdate': '20090101', 'edate': '20121231' }
timer.start()
request = acis.MultiStnDataRequest(params)
timer.stop()
# for record in request:
#	print record
# print request.meta
print '%d records (%.3f seconds)' % (len(request), timer.elapsed)
