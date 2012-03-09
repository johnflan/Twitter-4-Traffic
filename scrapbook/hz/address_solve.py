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
    #print jsonObj['results'][0]['geometry']['location']['lat']
    lat = jsonObj['results'][0]['geometry']['location']['lat']
    #print jsonObj['results'][0]['geometry']['location']['lng']
    lng = jsonObj['results'][0]['geometry']['location']['lng']
    return (lat,lng)

currRegex = addressRegex

def get_db_geo(conn, cursor,addr):
    query1 = "SELECT ST_AsText(latlon) as latlon FROM geolookup WHERE streetaddress ='"+str(addr)+"'"
    cursor.execute(query1)
    try:
        ((latlon,),) = cursor.fetchall()
        return latlon
    except:
        return 0

configSection = "Local database"
Config = ConfigParser.ConfigParser()
Config.read("../t4t_credentials.txt")
cfg_username = Config.get(configSection, "username")
cfg_password = Config.get(configSection, "password")
cfg_database = Config.get(configSection, "database")
cfg_server = Config.get(configSection, "server")

conn = DBAPI.connect(host=cfg_server, database=cfg_database,user=cfg_username, password=cfg_password)
cursor = conn.cursor()

#gmaps = GoogleMaps("ABQIAAAAUGnYtZ9Py2CWqhKA2j8WNhSV67USoQ6pUbqiV9eqnAi_hHG1PhShAENkss9dydHdndy0C9ko99g-Pg")
#query = "select text from tweets"
query = "select text from geolondon"

N = 10000
addresses = {}

cursor.execute(query)
counter = 0
commit = 0
for row in cursor:
    #i#uname = str(row[0])
    text = str(row[0])
    regexMatch = re.search(currRegex, text, re.IGNORECASE)
    if not regexMatch == None:
        #print text[:140]
        addr = regexMatch.group(0)[3:] #, text[:80]
        addr = addr.strip(punctuation).lower().strip()
        if ("the street" in addr) or ("my street" in addr) or ("this street" in addr) or ("our street" in
                addr) or ("a street" in addr) or ("high street" in addr) or ("upper st" in addr) or ("car park" in addr) or ("the park" in addr) or ("in every" in addr):
            continue;
        counter = counter + 1
        addresses[addr] = addresses.get(addr, 0) + 1
        #print addr

top_addr = sorted(addresses.iteritems(), key=itemgetter(1), reverse=True)[:N]
for addr, frequency in top_addr:
    try:
        #if not get_db_geo(conn,cursor,addr) == 0:
        print addr
        rows = get_db_geo(conn,cursor,addr)
        latitude = str(rows[6:15].replace(')',''))
        longitude = str( rows[16:26].replace(')',''))
            
        print "latitude is: "+ latitude+", longitude: "+longitude+"\n"
        print "*****************"
        continue
    except:
        print "no exists goto google"
    #try:
    #    query1 = "SELECT latlon FROM geolookup WHERE streetaddress ='"+str(addr)+"'"
    #print query1
    #cursor.execute(query1)
    #print "exe q1 success"
    #paddr = cursor.fetchall()
    #print paddr
    #print "success"
    #except:
        #print "lost"
        
    try:
        if get_db_geo(conn,cursor,addr)== 0:
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

   # for i in cursor:
    #    if i == None:
    #loc = "ST_GeographyFromText('SRID=4326;POINT("+str(lat)+" "+str(lon)+")')"
     #       lat,lng=geocode(address = addr + ", london",sensor = "false")
      #  else:
       #     print "it exsits"
    #lat,lng = gmaps.address_to_latlng(addr + ", london")
    #print addr + ":" + str(frequency) + ":" + str(lat) + ":" + str(lng)
#conn.commit()

print "\n", counter, "addresses identified."
print "\n", commit, "addresses commited"
