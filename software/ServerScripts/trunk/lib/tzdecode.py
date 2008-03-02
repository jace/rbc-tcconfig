#/usr/bin/env python

"""
This module provides a ``tzdecode`` function that will attempt to convert a
provided timezone into a ``tzinfo`` object. Returns None if the timezone
could not be parsed.
"""

from datetime import datetime, timedelta
import pytz

class NewFixedOffset(pytz._FixedOffset):
    """
    Class to return an empty dst, because Python's datetime module complains
    about None being unacceptable for tzinfo.dst(), which is unfortunately
    what pytz._FixedOffset.dst() returns.
    """
    def dst(self, dt):
        return timedelta()

def _offset_decode(timezone):
    """
    >>> _offset_decode('0100')
    60
    >>> _offset_decode('0130')
    90
    >>> _offset_decode('02:00')
    120
    >>> _offset_decode('05')
    300
    >>> _offset_decode('05:30')
    330
    """
    if timezone.find(':') != -1:
        hours, minutes = [int(x) for x in timezone.split(':')]
        return hours*60 + minutes
    elif len(timezone) <= 2:
        return int(timezone)*60 # Just hours
    elif len(timezone) <= 4:
        minutes = int(timezone[-2:])
        hours = int(timezone[:-2])
        return hours*60 + minutes

def tzdecode(timezone):
    """
    >>> tzdecode('+0530')
    pytz.FixedOffset(330)
    >>> tzdecode('0530')
    pytz.FixedOffset(330)
    >>> tzdecode('-0530')
    pytz.FixedOffset(-330)
    >>> tzdecode('+5')
    pytz.FixedOffset(300)
    >>> tzdecode('+05')
    pytz.FixedOffset(300)
    >>> tzdecode('GMT')
    <StaticTzInfo 'GMT'>
    >>> tzdecode('utc')
    <UTC>
    >>> tzdecode('Asia/Calcutta').zone
    'Asia/Calcutta'
    """
    timezone = str(timezone)
    if not timezone:
        return None
    if timezone.startswith('GMT') or timezone.startswith('UTC'):
        timezone = timezone[3:]
    if timezone.startswith('+') or timezone.startswith('-'):
        # Looks like a time offset. Decode
        try:
            offset = _offset_decode(timezone[1:])
        except: # Catch all
            return None
        if timezone.startswith('-'):
            offset = -offset
        return NewFixedOffset(offset)
    elif timezone[0] in [str(x) for x in range(10)]:
        # Starts with a number. Maybe it's a positive zone?
        try:
            offset = _offset_decode(timezone)
        except:
            return None
        return NewFixedOffset(offset)
    else:
        try:
            return pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            return None

def now(timezone):
    return datetime.now(tz=tzdecode(timezone))

if __name__=='__main__':
    import doctest
    doctest.testmod()
