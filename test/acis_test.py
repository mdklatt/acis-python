#!/usr/bin/python

# Standard modules.

import os.path
import sys


# Local modules.

import utillib.chron as chron


# Test module.

root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, root_dir)
import acis


timer = chron.Timer()

print 'StnMeta'
params = { 'climdiv': 'OK01', 'meta': ( 'uid', 'name' ) }
request = acis.Request('StnMeta')
timer.start()
result = acis.StnMetaResult(request.submit(params))
timer.stop()
# print result.meta
print '%d records (%.3f seconds)' % (len(result.meta), timer.elapsed)


print 'StnDataRequest'
params = { 'sid': '340027', 'sdate': '20090101', 'edate': '20121231',
   'elems': [ {'name': 'maxt' },  { 'name': 'mint' } ],
   'meta': ( 'uid', 'name' ) }
request = acis.Request('StnData')
timer.start()
result = acis.StnDataResult(request.submit(params))
timer.stop()
# for record in result:
#     print record
# print result.meta
print '%d records (%.3f seconds)' % (len(result), timer.elapsed)


print 'StnData (large)'
elems = [{'name': elem} for elem in ('mint', 'maxt', 'obst', 'pcpn', 'snow',
    'snwd')]
params = { 'sid': '344451', 'sdate': 'por', 'edate': 'por', 'elems': elems,
    'meta': ('uid', 'name') }
request = acis.Request('StnData')
timer.start()
result = acis.StnDataResult(request.submit(params))
timer.stop()
# for record in result:
#     print record
# print result.meta
print '%d records (%.3f seconds)' % (len(result), timer.elapsed)


print 'MultiStnData'
params = { 'sids': ('340017', '340027'), 'sdate': '20090101',
    'edate': '20121231', 'elems': [ {'name': 'maxt' },  { 'name': 'mint' } ],
    'meta': ( 'uid', 'name' ) }
request = acis.Request('MultiStnData')
timer.start()
result = acis.MultiStnDataResult(request.submit(params))
timer.stop()
# for record in result:
#   print record
# print result.meta
print '%d records (%.3f seconds)' % (len(result), timer.elapsed)


print 'MultiStnData (reductions)'
maxt = { 'name': 'maxt', 'interval': 'mly', 'duration': 'mly',
    'reduce': { 'reduce': 'min', 'add': 'date' } }
pcpn = {'name': 'pcpn', 'interval': 'mly', 'duration': 'ytd',
    'reduce': { 'reduce': 'sum', 'add': 'mcnt' } }
params = { 'sids': ( '340017', '340027' ), 'meta': ( 'uid', 'name' ),
    'elems': ( maxt, pcpn ), 'sdate': '20090101', 'edate': '20121231' }
request = acis.Request('MultiStnData')
timer.start()
result = acis.MultiStnDataResult(request.submit(params))
timer.stop()
# for record in result:
#   print record
# print result.meta
print '%d records (%.3f seconds)' % (len(result), timer.elapsed)
