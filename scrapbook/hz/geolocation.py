import ConfigParser
import pg8000
from pg8000 import DBAPI
import re
from googlemaps  import GoogleMaps

gmaps = GoogleMaps("ABQIAAAAUGnYtZ9Py2CWqhKA2j8WNhSV67USoQ6pUbqiV9eqnAi_hHG1PhShAENkss9dydHdndy0C9ko99g-Pg")

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
cursor.execute(query)

regex = "(\sin|\son|\sat)([\w\s]+){1,5}(street|road|bridge|market|ave|square)"
address = ""
total = 0
for row in cursor:
    text = str(row[0])
    m = re.search(regex,text)
    if not m ==None:
#    try:
        print m.group(0)
#        #rint text[m.start():m.end()]
#        #ddress = text[m.start():m.end()]
        total = total+1
#    #except AttributeError:
#     #   print "error"
#
#   # try:
#        #lat, lng = gmaps.address_to_latlng(address+"UK")
#        #print lat,lng
#    #except:
#        #print "there is no such address"
