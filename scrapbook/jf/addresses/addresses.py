#!/bin/bash

import ConfigParser
from string import punctuation
from operator import itemgetter
import pg8000
from pg8000 import DBAPI
import re

#postcodeRegex = "(GIR 0AA)|(((A[BL]|B[ABDHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9]|((E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(SW|W)([2-9]|[1-9][0-9])|EC[1-9][0-9]) [0-9][ABD-HJLNP-UW-Z]{2})"

#addressRegex = r"(\b(at|on)\s\w+\s(st(reet)?|r[(od)]d)[.,\b](station|market))" 
addressRegex = r"(\b(at|on)\s((\d+|\w{2,})\s){1,3}(st(reet)?|r[(oa)]d|bridge|ave(nue)?)(\sstation|\smarket|\sjct|\sjunction)?[,.\s])" 

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
        lraddr = addr.lower()
        if ("the street" in lraddr) or (" my " in lraddr) or (" this " in lraddr) or ("our street" in
                lraddr) or ("a street" in lraddr) or ("high street" in lraddr) or ("upper st" in lraddr) :
            continue;
        counter = counter + 1
        addr = addr.strip(punctuation).lower().strip()
        addresses[addr] = addresses.get(addr, 0) + 1
        #print addr

top_addr = sorted(addresses.iteritems(), key=itemgetter(1), reverse=True)[:N]
for addr, frequency in top_addr:
    print "%s: %d" % (addr, frequency)


print "\n", counter, "addresses identified."
