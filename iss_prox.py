#!/usr/bin/env python3
# import json
# Reads current location of ISS as JSON file
# then uses Great Circle calc to determine distance
# to fixed location
import requests, json
from math import radians, cos, sin, asin, sqrt

def getISS():
# Home
# Dunedin, NZ
	Hlon = 170.537514
	Hlat = -45.8516929
# ISS
	ISS = requests.get("http://api.open-notify.org/iss-now.json")
	ISStext = ISS.text
	ISSjson = json.loads(ISStext)
	ISSlat = float(ISSjson['iss_position']['latitude'])
	ISSlong = float(ISSjson['iss_position']['longitude'])
	return int(haversine(ISSlat, ISSlong, Hlat, Hlon))

def haversine(lat1, lon1, lat2, lon2):
	R = 6372.8 #km

	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))

	return R * c

# Distance in Kms
print('Distance to ISS is', getISS(), 'Kms')
