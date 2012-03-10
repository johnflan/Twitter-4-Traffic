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

currRegex = addressRegex

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
query = "select text from tweets"
#query = "select text from geolondon"
query2 = "INSERT INTO geolookup (streetaddress,latlon)VALUES('South kensington station', ST_GeographyFromText('SRID=4326;POINT(50.000 -0.0000000)'))"

N = 10000
addresses = {}
cursor.execute(query2)
#print "selected %s rows", cursor.numrows
conn.commit()

#cursor1 = conn.cursor()
#top_addr = sorted(addresses.iteritems(), key=itemgetter(1), reverse=True)[:N]
#for addr, frequency in top_addr:
    #print "%s: %d" % (addr, frequency)
 #   print addr
  #  try:
   #     query1 = "SELECT latlon FROM geolookup WHERE streetaddress ='"+str(addr)+"'"
    #    print query1
     #   cursor1.execute(query1)
      #  paddr = cursor.fetchall()
       # print paddr
        #print "success"
   # except:
    #    print "lost"
        
    #try:
        #print geocode(address = addr+", london", sensor = "false")
     #   lat,lon, = geocode(address = addr+",london", sensor = "false")
      #  print lat
       # print lon
       # geoloc = "ST_GeographyFromText('SRID=4326;POINT("+str(lat)+" "+str(lon)+")')"
    #query2 = "INSERT INTO geolookup (streetaddress,latlon)VALUES('"+str(addr)+"',"+geoloc+")"
       # qurey2 = "INSERT INTO geolookup (streetaddress,latlon)VALUES('South kensington station', ST_GeographyFromText('SRID=4326;POINT(50.000 -0.0000000)'))"
       # print query2
       # cursor1.execute(query2)
       # print "insert success"
   # except:
    #    print "fail"
     #   continue

   # for i in cursor:
    #    if i == None:
    #loc = "ST_GeographyFromText('SRID=4326;POINT("+str(lat)+" "+str(lon)+")')"
     #       lat,lng=geocode(address = addr + ", london",sensor = "false")
      #  else:
       #     print "it exsits"
    #lat,lng = gmaps.address_to_latlng(addr + ", london")
    #print addr + ":" + str(frequency) + ":" + str(lat) + ":" + str(lng)


#26;POINT(50.000 -0.0000000)'))print "\n", counter, "addresses identified."
