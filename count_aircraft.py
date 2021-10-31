#!/usr/bin/env python3
# import json
# Uses FlightAware JSON feed for aircraft data then
# WLED JSON put to control Neopixel string of 50 leds
# laid out in 5 rows of 10
# GEH Oct 2021
import requests, json
import time
import datetime
from math import radians, cos, sin, asin, sqrt

# store the URL in url as parameter for urlopen
true = True
false = False
# prepare WLED call
url_json = 'http://10.1.1.162/json'
url_off = 'http://10.1.1.162/win&T=0'
WLEDHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}

###########################  ISS parts ###########
def getISS():
# Home
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

# Distance in Kms, usage
#print('Distance to ISS is', getISS(), 'Kms')

###########################  ISS parts ###########

# intheair = 3

while(True):
	now = datetime.datetime.now()
	if now.hour > 5 and now.hour < 23:
		try: # just in case
			url_ff = requests.get("http://10.1.1.188/skyaware/data/aircraft.json")
# store the response of URL
			text = url_ff.text
# storing the JSON response from url in data
			data = json.loads(text)
			intheair = len(data['aircraft'])-1 # exclude Mt Cargill ground station
#		intheair = 2
		except:
			intheair = 0
		print(str(intheair) + ' aircraft seen')
# ignore the ground station on Mt Cargill and run between 6am and 11pm
		if intheair > 0:
# 			clear last loop
			payload={"on":False}
			try:
				WLEDresponse= requests.post(url_json,data=json.dumps(payload),headers=WLEDHeaders)
			except:
				print('failed to reset WLED')
#			print(WLEDresponse)
#			print("new loop")
			if intheair > 10:
				palette=35 #reds
			elif intheair > 5:
				palette=50 #greens
			else:
				palette = 36 #blues
			for xloop in range(5): #Note if intheair is 3 then seq is 0-2
					x=xloop+1
					seg_no = x 
					seg_start = xloop * 10
					seg_end = seg_start + 10 
#					print(str(xloop),str(x),str(seg_no),str(seg_start),str(seg_end))
					rows = intheair % 5
					if rows == 0:
						rows = 5 # when getting 5, 10, 15 
					if x <= rows:
						show = True
					else:
						show = False
					payload={"on":True,"bri":128,"transition":7,"mainseg":0,"seg":[{"id":0,"start":0,"stop":50,"len":50,"grp":1,"spc":0,"on":False},{"id":seg_no,"start":seg_start,"stop":seg_end,"len":10,"grp":1,"spc":0,"on":show,"bri":255,"col":[[102,153,0],[0,0,0],[0,0,0]],"fx":67,"sx":65,"ix":113,"pal":palette,"sel":True,"rev":False,"mi":False}]}
#					print(payload)
					try:
						WLEDresponse= requests.post(url_json,data=json.dumps(payload),headers=WLEDHeaders)
					except:
						print('failed to set WLED')
#					print(WLEDresponse)
		else:
			payload={"on":False}
			try:
				WLEDresponse= requests.post(url_json,data=json.dumps(payload),headers=WLEDHeaders)
			except:
				print('failed to blank WLED')
		time.sleep(5)
# Check for ISS
		if getISS() < 200:
# 87 is glitter
			payload={"on":True,"bri":128,"transition":7,"mainseg":0,"seg":[{"id":0,"start":0,"stop":50,"len":50,"grp":1,"spc":0,"on":True}],"fx":87,"sx":65,"pal":0,"sel":True,"rev":False,"mi":False}
			try:
				WLEDresponse= requests.post(url_json,data=json.dumps(payload),headers=WLEDHeaders)
			except:
				print('failed to set WLED')
