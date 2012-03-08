#!/bin/bash

import ConfigParser
from string import punctuation
from operator import itemgetter
from googlemaps import GoogleMaps
import pg8000
from pg8000 import DBAPI
import re

#postcodeRegex = "(GIR 0AA)|(((A[BL]|B[ABDHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9]|((E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(SW|W)([2-9]|[1-9][0-9])|EC[1-9][0-9]) [0-9][ABD-HJLNP-UW-Z]{2})"

#addressRegex = r"(\b(at|on)\s\w+\s(st(reet)?|r[(od)]d)[.,\b](station|market))" 
addressRegex = r"(\b(in|at|on|\w,)\s((\d+|\w{2,})\s){1,3}(st(reet)?|r[(oa)]d|bridge|ave(nue)?|park){1,2}(\sstation|\smarket)?[,.\s$]{1})" 

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

gmaps = GoogleMaps("ABQIAAAAUGnYtZ9Py2CWqhKA2j8WNhSV67USoQ6pUbqiV9eqnAi_hHG1PhShAENkss9dydHdndy0C9ko99g-Pg")
#query = "select text from tweets"
query = "select text from geolondon"

N = 10000
addresses = {}

cursor.execute(query)
counter = 0
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
    #print "%s: %d" % (addr, frequency)
    lat,lng = gmaps.address_to_latlng(addr + ", london")
    print addr + ":" + frequency + ":" + lat + ":" + lng


print "\n", counter, "addresses identified."
