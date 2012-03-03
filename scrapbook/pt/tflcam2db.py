from pg8000 import DBAPI
from xml.dom.minidom import parseString
from math import *
import sys
import optparse
import ConfigParser
import time
from time import strftime
import urllib2

def main(**kw):
    # Connect to the db
    db = dict([[k,v] for k,v in kw.iteritems() if k!='email' and k!='feedid'])
    cursor, conn = connect(**db)

    periodically_sample_feed(cursor, conn, **kw)

###############################################################################################
############################ Creates a connection to the db ###################################
###############################################################################################

def connect(**db):
    try:
        # get a connection, if a connect cannot be made an exception will be raised here
        conn = DBAPI.connect(**db)
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Database connection failed! -> %s" % (exceptionValue))
    return cursor,conn

###############################################################################################
############################# Loads a camera feed from tfl ####################################
###############################################################################################

def periodically_sample_feed(cursor, conn, **kw):
    url = 'http://www.tfl.gov.uk/tfl/businessandpartners/syndication/feed.aspx?email=%s&feedid=%s' % (kw['email'], kw['feedid'])
    refresh = 300
    while True:
        try:
            tStart = time.time()
            
            req = urllib2.Request(url)
            data = urllib2.urlopen(req).read()
            dom = parseString(data.encode("ascii", "ignore"))

            store_tfl_data(cursor, conn, dom)
            
            tEnd = time.time()
            remain = refresh - ( tEnd - tStart )
            print "TfL Camera Feed Stored @%s" % updated_at
            print "Sleeping For", remain, "Seconds"
            if remain > 0: time.sleep(remain)
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Error -> %s" % (exceptionValue)
            time.sleep(refresh)

###############################################################################################
########################### Store the tfl feed in the database ################################
###############################################################################################

def store_tfl_data(cursor, conn, dom):
    cameras = dom.getElementsByTagName('kml')[0].getElementsByTagName('Cameras')[0].getElementsByTagName('Camera')

    cursor.execute("DELETE FROM cameras")    

    for camera in cameras:
        cam = {}
        cam['title'] = camera.getElementsByTagName("title")[0].firstChild.data
        cam['link'] = camera.getElementsByTagName("Link")[0].firstChild.data
        cam['placemarkname'] = camera.getElementsByTagName("Placemark")[0].getElementsByTagName("name")[0].firstChild.data
        cam['placemarkdescription'] = camera.getElementsByTagName("Placemark")[0].getElementsByTagName("description")[0].firstChild.data
        cam['geolocation'] = camera.getElementsByTagName("Placemark")[0].getElementsByTagName("Point")[0].getElementsByTagName("Coordinates")[0].firstChild.data
        cursor, conn = updatecam(cursor, conn, **cam)

    conn.commit()

def updatecam(cursor, conn, **cam):
    lon,lat = cam['geolocation'].split(',')
    geoValue = "ST_GeographyFromText('SRID=4326; POINT(%s %s)'))" % (lon, lat)
    
    try:
        queryColumns = "("
        queryValues = " VALUES("

        for key in rrevent:
            queryColumns+="%s," % key
            if(rrevent[key]!='NULL'): queryValues+="'%s'," % rrevent[key]
            else: queryValues+="NULL,"

        queryColumns += "lonlat)"
        query_archive = "INSERT INTO archive" + queryColumns + queryValues + geoValue

        cursor.execute(query_archive)

        query_tfl = "INSERT INTO tfl" + queryColumns + queryValues + geoValue
        cursor.execute(query_tfl)
        return cursor, conn
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        print "Insert failed! -> %s" % (exceptionValue)

if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")

    configSection = "TfL feed"
    email = Config.get(configSection, "email")
    feedid = Config.get(configSection, "camfeedid")

    # Parse options from the command line
    parser = optparse.OptionParser("usage: %prog [options]")
    parser.add_option('-H','--host',
                    dest='host',
                    default=host,
                    help='The hostname of the DB')
    parser.add_option('-d','--database',
                    dest='database',
                    default=database,
                    help='The name of the DB')
    parser.add_option('-u','--user',
                    dest='user',
                    default=user,
                    help='The username for the DB')
    parser.add_option('-p','--password',
                    dest='password',
                    default=password,
                    help='The password for the DB')
    parser.add_option('-e','--email',
                    dest='email',
                    default=email,
                    help='The email for the TfL feed')
    parser.add_option('-f','--feedid',
                    dest='feedid',
                    default=feedid,
                    help='The for the TfL feed')
    (options, args) = parser.parse_args()

    kw = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    sys.exit(main(**kw))

