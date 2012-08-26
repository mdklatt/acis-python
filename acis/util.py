"""
ACIS utility functions.

"""
__version__ = '0.1.dev'
__all__ = ('parse_sid',)

import re

sid_types = {
    1: 'WBAN',
    2: 'COOP',
    3: 'FAA',
    4: 'WMO',
    5: 'ICAO',
    6: 'GHCN',
    7: 'NWSLI',
    8: 'RCC',
    9: 'ThreadEx',
    10: 'CoCoRaHS',
}
sid_regex = re.compile(r'(^[^ ]*) (\d+)$')
def parse_sid(sid):
    try:
        id, code = sid_regex.search(sid).groups()
    except AttributeError:  # search returned None
        raise ValueError('not a valid sid')
    try:
        return id, sid_types[int(code)]
    except KeyError:
        raise ValueError('unknown sid type')
