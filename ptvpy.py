'''
Unofficial Python wrapper for Public Transport Victoria API
Read the full API documentation here: http://stevage.github.io/PTV-API-doc/

Documentation in "quotes" here is verbatim from PTV.
Source: Licensed from Public Transport Victoria under a Creative Commons Attribution 3.0 Australia Licence.

This Python module itself is licensed under WTFPL.

To use it, rename the included apikey.example to apikey.py and include your API key and DevID.
Don't have one? Email APIKeyRequest@ptv.vic.gov.au with subject "PTV Timetable API - request for key"

Dependencies:

sudo pip install python-dateutil

'''

import datetime
import json
from urllib.parse import quote
from urllib.parse import urlencode
from urllib.request import urlopen

import apikey  # This file must define devid and key


def nownomicro():
    ''' Returns current time, without microseconds, as required by PTV API.'''
    return datetime.datetime.utcnow().replace(microsecond=0)


def now8601():
    ''' Returns current time, without microseconds, as required by PTV API, in 8601 format.'''
    return nownomicro().isoformat()


def callAPI(api, args={}):
    ''' Makes the specified API call, handling signature computation and developer id.'''
    import hmac, hashlib
    ptvbase = 'https://timetableapi.ptv.vic.gov.au'
    preamble = '/v3/'
    args['devid'] = apikey.devid
    key = apikey.devkey
    encodedKey = str.encode(key)
    call = preamble + api + "?" + urlencode(args)
    encodedCall = str.encode(call)

    sig = hmac.new(key=encodedKey, msg=encodedCall, digestmod=hashlib.sha1).hexdigest().upper()
    url = ptvbase + call + "&signature=" + sig
    print(url)
    response = urlopen(url)

    return json.load(response)


def routeTypes():
    return callAPI("route_types")


def stopsByLatLang(latitude, longitude):
    '''Stops Nearby returns up to 30 stops nearest to a specified coordinate."'''
    # stopsNearby(-38, 145)
    return callAPI("stops/location/%d,%d" % (latitude, longitude))


def stopsByStopIdAndRoute(stopid, routeType):
    return callAPI("stops/%d/route_type/%d" % (stopid, routeType))


def departures(stopid, routeType):
    # rJson = callAPI("departures/route_type/%d/stop/%d" %(routeType,stopid))
    # rData = json.loads(rJson)
    # utc = rdata['departures']
    return callAPI("departures/route_type/%d/stop/%d" % (routeType, stopid))


# def transportPOIsByMap(poi, lat1, long1, lat2, long2, griddepth, limit):
#     '''"Transport POIs by Map returns a set of locations consisting of stops and/or myki ticket outlets
#     (collectively known as points of interest - i.e. POIs) within a region demarcated on a map through
#     a set of latitude and longitude coordinates.
#     POI codes:
#       0 Train (metropolitan)
#       1 Tram
#       2 Bus (metropolitan and regional, but not V/Line)
#       3 V/Line regional train and coach
#       4 NightRider
#       100 Ticket outlet
#     "'''
#
#     # transportPOIsByMap(2,-37,145,-37.5,145.5,3,10)
#     return callAPI("poi/%s/lat1/%d/long1/%d/lat2/%d/long2/%d/griddepth/%d/limit/%d" %
#                    (str(poi), lat1, long1, lat2, long2, griddepth, limit))
# note: this has been replaced by search in v3

def search(query):
    '''"The Search API returns all stops and lines that match the input search text."'''
    # search("Hoddle St")

    return callAPI("search/" + quote(str(query)))


# TODO: convert incoming dates to datetimes, using dateutil.parser
# def broadNextDepartures(mode, stop, limit, for_utc=nownomicro()):
#     '''"Broad Next Departures returns the next departure times at a prescribed stop irrespective of the line and direction of the service. For example, if the stop is Camberwell Station, Broad Next Departures will return the times for all three lines (Belgrave, Lilydale and Alamein) running in both directions (towards the city and away from the city)."
#     Note: since the result is wrapped in a 'values' object, we return the contents of that object.
#     '''
#     # This and all functions that have a 'mode' argument also allow strings: train,tram,bus,vline,nightrider
#     # broadNextDepartures(0,1104,2)
#     # Note: for_utc is undocumented.
#
#     return callAPI("mode/%d/stop/%d/departures/by-destination/limit/%d" % (modeFromString(mode), stop, limit),
#                    {"for_utc": for_utc.isoformat()})['values']
#
# NOTE: REPLACED BY DEPARTURES IN V3

def specificNextDepartures(stopid, routeType, routeid):
    '''"Specific Next Departures returns the times for the next departures at a prescribed stop for a specific mode, line and direction. For example, if the stop is Camberwell Station, Specific Next Departures returns only the times for one line running in one direction (for example, the Belgrave line running towards the city)."'''
    # specificNextDepartures(1,1881,2026,24,1)

    return callAPI("departures/route_type/%d/stop/%d/route/%d" % (routeType, stopid, routeid))


def Patterns(runid, routeType, for_utc=nownomicro()):
    ''' "The Stopping Pattern API returns the stopping pattern for a specific run (i.e. transport service) from a prescribed 
    stop at a prescribed time. The stopping pattern is comprised of timetable values ordered by stopping order."'''
    # stoppingPattern(0,4780,1104)
    # /v2/mode/%@/run/%@/stop/%@/stopping-pattern?for_utc=%@&devid=%@&signature=%@
    return callAPI("pattern/run/%d/route_type/%d" % (runid, routeType))


def stopsOnALine(routeid, routeType):
    '''"The Stops on a Line API returns a list of all the stops for a requested line, ordered by location name.
    '''
    # stopsOnALine(4,'1818')
    return callAPI("stops/route/%d/route_type/%d" % (routeid, routeType))


def disruptions():
    return callAPI("disruptions")


### End official part. Now higher level functions.

def modeFromString(modestr):
    # Allows you to pass string modes to the API rather than their 0,1,2,3 etc.
    # Mode:  0 Train (metropolitan)
    #       1 Tram
    #       2 Bus (metropolitan and regional, but not V/Line)
    #       3 V/Line train and coach
    #       4 NightRider
    if type(modestr) == type(0):
        return modestr
    return ['train', 'tram', 'bus', 'vline', 'nightrider'].index(modestr)


def melbourneTime(isostr):
    from dateutil import parser, tz
    d = parser.parse(isostr)
    d.replace(tzinfo=tz.gettz('UTC'))  # Not sure if needed
    return d.astimezone(tz.gettz('Australia/Melbourne'))


def findThing(name, stoporline, transport_type=''):
    out = []
    for x in search(name):
        if x['type'] != stoporline:
            continue
        r = x['result']
        if transport_type not in ('', r['transport_type']):
            continue
        r.pop('distance', None)
        out += [r]
    return out


def findLine(name, transport_type=''):
    return findThing(name, 'line', transport_type)


def findStop(name, transport_type=''):
    return findThing(name, 'stop', transport_type)
    # transport_type: bus, vline, train, tram [vline is both coach and train!]
    # Very broad queries (eg 'Railway Station') seem to return incomplete sets.
    # stops = filter(lambda x: x['type'] == 'stop', search(name))
    # stops = map(lambda x: x['result'], stops)
    # if transport_type:
    #  stops = filter(lambda x: x['transport_type'] == transport_type, stops)
    # return stops
