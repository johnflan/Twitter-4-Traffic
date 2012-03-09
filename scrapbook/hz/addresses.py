#!/bin/bash

import ConfigParser
import pg8000
from pg8000 import DBAPI
import re
from googlemaps import GoogleMaps

addressRegex = r"(\b(at|on)\s((\d+|\w{2,})\s){1,2}(st(reet)?|r[(oa)]d)(\sstation|\smarket)?[,.\s])"
#addressRegex =r"(\b(at|on)\s((\d+|\w{2,})\s){1,2}(st(reet)?|r[(oa)]d)(\sstation|\smarket)?)"

currRegex = addressRegex

gmaps = GoogleMaps("ABQIAAAAUGnYtZ9Py2CWqhKA2j8WNhSV67USoQ6pUbqiV9eqnAi_hHG1PhShAENkss9dydHdndy0C9ko99g-Pg")
#gmaps = GoogleMaps("AIzaSyCw6F9tfQG6R56y9tUUm4WaI7o-D3cn7HI")

conn = DBAPI.connect(host=cfg_server, database=cfg_database,user=cfg_username, password=cfg_password)
cursor = conn.cursor()

query = "select text from tweets where geolocation is null"

cursor.execute(query)
counter = 0
for row in cursor:
    text = str(row[0])
    regexMatch = re.search(currRegex, text, re.IGNORECASE)
    if not regexMatch == None:
        #print text[:140]
        addr = regexMatch.group(0)[3:] #, text[:80]
        lraddr = addr.lower()
        if ("the street" in lraddr) or ("my street" in lraddr) or ("this street" in lraddr) or ("our street" in
                lraddr) or ("a street" in lraddr) or ("high street" in lraddr) or ("upper st" in lraddr) :
            continue;

        try:
            lat,lng = gmaps.address_to_latlng(addr+" London")
            counter = counter + 1
            print addr, lat, lng
        except:
            print addr, "there is no address detected"


        if counter > 1400:
            break

print "\n", counter, "addresses identified."
