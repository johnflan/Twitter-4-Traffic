#!/bin/bash

import ConfigParser
import pg8000
from pg8000 import DBAPI
import re

#postcodeRegex = "(GIR 0AA)|(((A[BL]|B[ABDHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9]|((E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(SW|W)([2-9]|[1-9][0-9])|EC[1-9][0-9]) [0-9][ABD-HJLNP-UW-Z]{2})"

#addressRegex = r"(\b(at|on)\s\w+\s(st(reet)?|r[(od)]d)[.,\b](station|market))" 
addressRegex = r"((traffic)\s(in|near|into)\s((\w{4,})(\s(\w{10,}))?)[,.\s$]{1})" 

currRegex = addressRegex

configSection = "Local database"
Config = ConfigParser.ConfigParser()
Config.read("../../t4t_credentials.txt")
cfg_username = Config.get(configSection, "username")
cfg_password = Config.get(configSection, "password")
cfg_database = Config.get(configSection, "database")
cfg_server = Config.get(configSection, "server")

conn = DBAPI.connect(host=cfg_server, database=cfg_database,user=cfg_username, password=cfg_password)
cursor = conn.cursor()

query = "select uname, text from tweets where geolocation is null"

cursor.execute(query)
counter = 0
for row in cursor:
    uname = str(row[0])
    text = str(row[1])
    regexMatch = re.search(currRegex, text, re.IGNORECASE)
    if not regexMatch == None:
        #print text[:140]
        addr = regexMatch.group(4)
        lraddr = addr.lower()
        if ("traffic in london" in lraddr) or ("traffic in west london" in lraddr) or ("traffic in central london" in lraddr) or ("traffic in south london" in
                lraddr) or ("traffic in north london" in lraddr) or ("high street" in lraddr) or ("upper st" in lraddr) :
            continue;
        print lraddr
        counter = counter + 1
        if counter > 1400:
            break

print "\n", counter, "addresses identified."
