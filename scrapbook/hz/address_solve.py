#!/bin/bash

import ConfigParser
from string import punctuation
from operator import itemgetter
from googlemaps import GoogleMaps
import pg8000
from pg8000 import DBAPI
import re
import urllib
import simplejson
import sys
import urllib2
from json import JSONDecoder
import  json

addressRegex = r"(\b(in|at|on|\w,)\s((\d+|\w{2,})\s){1,3}(st(reet)?|r[(oa)]d|bridge|ave(nue)?|park){1,2}(\sstation|\smarket)?[,.\s$]{1})" 

GEOCODE_BASE_URL = "http://maps.googleapis.com/maps/api/geocode/json"

###############################################################################################
################################ Connects to the database #####################################
###############################################################################################

def main():
	connect()
		
	N = 10000
	addresses = {}
	counter = 0
	commit = 0
	
	# Fetch the tweets which don't have geolocation
	query = "select tid,text from tweets where geolocation is null"
	cursor.execute(query)

	for row in cursor:

		text = str(row[0])
		
		# Check if the tweet contains the regex
		regexMatch = re.search(currRegex, text, re.IGNORECASE)
		
		if not regexMatch == None:

			addr = regexMatch.group(0)[3:] 
			addr = addr.strip(punctuation).lower().strip()
			
			if ("the street" in addr) or ("my street" in addr) or ("this street" in addr) or ("our street" in
					addr) or ("a street" in addr) or ("high street" in addr) or ("upper st" in addr) or ("car park" in addr) or ("the park" in addr) or ("in every" in addr):
				continue
				
			counter = counter + 1
			addresses[addr] = addresses.get(addr, 0) + 1

	top_addr = sorted(addresses.iteritems(), key=itemgetter(1), reverse=True)[:N]
	
	for addr in top_addr:
		
		# Try to find the corresponding geolocation in the local table geolookup
		try:
			rows = get_db_geo(addr)
			latitude = str(rows[6:15].replace(')',''))
			longitude = str( rows[16:26].replace(')',''))
			
			geoloc = "ST_GeographyFromText('SRID=4326;POINT(" + longitude + " " + latitude + ")')"
			query = "UPDATE tweets SET geolocation=%s WHERE tid =%s" % ( geoloc,  )
			
			continue
		except:
			# There is no such an address in the geolookup table so go and try to add it
		
		try:
			lat,lon, = geocode(address = addr+",london", sensor = "false")
			geoloc = "ST_GeographyFromText('SRID=4326;POINT("+str(lat)+" "+str(lon)+")')"
			query2 = "INSERT INTO geolookup (streetaddress,latlon)VALUES('"+str(addr)+"',"+geoloc+")"
			cursor.execute(query2)
			conn.commit()
			commit = commit + 1
			print "insert success \n"
		except:
			print "fail \n"
			continue

print "\n", counter, "addresses identified."
print "\n", commit, "addresses commited"
	
###############################################################################################
################################ Connects to the database #####################################
###############################################################################################
    
def connect():
    global conn
    global cursor
    try:
        # Create a connection to the database
        conn = DBAPI.connect(**db)
        # Create a cursor that will be used to execute queries
        cursor = conn.cursor()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script/thread and print an error telling what happened.
        print "Database connection failed! -> %s" % (exceptionValue)
        sys.exit()
		
###############################################################################################
######## Parse the json file from google map and get lat and lon for the address ##############
###############################################################################################

def geocode(address,sensor, **geo_args):
    geo_args.update({
        "address":address,
        "sensor":sensor
        })
    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    req = urllib2.Request(url)
    result = urllib2.urlopen(req)
    response = result.read()
    decoder = json.JSONDecoder()
    jsonObj = decoder.decode(response)
    lat = jsonObj['results'][0]['geometry']['location']['lat']
    lng = jsonObj['results'][0]['geometry']['location']['lng']
    return (lat,lng)

currRegex = addressRegex

###############################################################################################
###### Get the lon and lat from the geolookup and match them with the addr if it exists #######
###############################################################################################

def get_db_geo(addr):
    query1 = "SELECT ST_AsText(latlon) as latlon FROM geolookup WHERE streetaddress ='"+str(addr)+"'"
    cursor.execute(query1)
    try:
        ((latlon,),) = cursor.fetchall()
        return latlon
    except:
        return 0	
		
###############################################################################################
######################### Executed if the script is run directly ##############################
###############################################################################################
    
if __name__ == "__main__":
    configSection="Local database"
    # Read the database values from a file
    Config = ConfigParser.ConfigParser()
    Config.read("../t4t_credentials.txt")
    
    db = dict()
    db['user'] = Config.get(configSection, "username")
    db['password'] = Config.get(configSection, "password")
    db['database'] = Config.get(configSection, "database")
    db['host'] = Config.get(configSection, "server")

	main()

