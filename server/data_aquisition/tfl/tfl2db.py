from pg8000 import DBAPI
from xml.dom.minidom import parseString
import sys
import optparse
import ConfigParser
import time
from time import strftime
import urllib2
from grid2lonlatConverter import grid2lonlat
import thread

###############################################################################################
############################ Creates a connection to the db ###################################
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
############################# Loads an xml feed from tfl ######################################
###############################################################################################

def sampleFeed():
    # Connect to the database
    connect()
    # The url for the tfl feed
    url = 'http://www.tfl.gov.uk/tfl/businessandpartners/syndication/feed.aspx?email=%s&feedid=%s' % (tfl['email'], tfl['eventfeedid'])
    refresh = 300
    while True:
        try:
            tStart = time.time()
            # Get the current time
            updated_at = strftime("%d/%m/%y %H:%M:%S")

            # Get the dom object
            req = urllib2.Request(url)
            data = urllib2.urlopen(req).read()
            dom = parseString(data.encode("ascii", "ignore"))

            # Store the dom object in the database
            storeTflData(dom, updated_at)

            # Get the refresh value specified in the dom object
            refresh = 60 * float(dom.getElementsByTagName('Header')[0].getElementsByTagName('RefreshRate')[0].firstChild.data)
            
            tEnd = time.time()
            # Find the time that remains until the next update
            remain = refresh - ( tEnd - tStart )
            print "TfL Feed Stored @%s" % updated_at
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

def storeTflData(dom, updated_at):
    events = dom.getElementsByTagName('roadrunner')[0].getElementsByTagName('rr_event')
    # Delete previous data from the table
    cursor.execute("DELETE FROM tfl")    

    # For every tfl event find each element
    for event in events:
        rrevent = {}
        rrevent['updated_at'] = updated_at
        rrevent['ltisid'] = event.getElementsByTagName("ltisid")[0].firstChild.data
        rrevent['eventstartdate'] = event.getElementsByTagName("eventstartdate")[0].firstChild.data
        rrevent['eventstarttime'] = event.getElementsByTagName("eventstarttime")[0].firstChild.data
        rrevent['eventenddate'] = event.getElementsByTagName("eventenddate")[0].firstChild.data
        rrevent['eventendtime'] = event.getElementsByTagName("eventendtime")[0].firstChild.data
        rrevent['event_type'] = event.getElementsByTagName("event_type")[0].firstChild.data
        rrevent['category'] = event.getElementsByTagName("category")[0].firstChild.data
        rrevent['title'] = event.getElementsByTagName("title")[0].firstChild.data
        rrevent['sector'] = event.getElementsByTagName("sector")[0].firstChild.data
        rrevent['location'] = event.getElementsByTagName("location")[0].firstChild.data
        rrevent['description'] = event.getElementsByTagName("description")[0].firstChild.data
        rrevent['lastmodifiedtime'] = event.getElementsByTagName("lastmodifiedtime")[0].firstChild.data
        rrevent['severity'] = event.getElementsByTagName("severity")[0].firstChild.data
        rrevent['PostCodeStart'] = event.getElementsByTagName("PostCodeStart")[0].firstChild.data
        rrevent['PostCodeEnd'] = event.getElementsByTagName("PostCodeEnd")[0].firstChild.data
        rrevent['remarkDate'] = event.getElementsByTagName("remarkDate")[0].firstChild.data
        rrevent['remarkTime'] = event.getElementsByTagName("remarkTime")[0].firstChild.data
        rrevent['remark'] = event.getElementsByTagName("remark")[0].firstChild.data
        rrevent['gridEasting'] = event.getElementsByTagName("gridEasting")[0].firstChild.data
        rrevent['gridNorthing'] = event.getElementsByTagName("gridNorthing")[0].firstChild.data
        # Insert the tfl event in the database
        updateEvent(**rrevent)

    # Commit all database changes after all events have been stored
    conn.commit()

###############################################################################################
########################### Update the tfl table of the database ##############################
###############################################################################################
    
def updateEvent(**rrevent):
    # If there is geolocation for the tfl event
    if rrevent['gridNorthing']!="NULL" and rrevent['gridEasting']!="NULL":
        lon, lat = grid2lonlat(float(rrevent['gridNorthing']), float(rrevent['gridEasting']))
        geoValue = "ST_GeographyFromText('SRID=4326; POINT(%s %s)'))" % (lon, lat)
    # If there is no geolocation use NULL
    else:
        geoValue = "NULL)"
    try:
        queryColumns = "("
        queryValues = " VALUES("

        for key in rrevent:
            rrevent[key] = rrevent[key].replace("'","''").replace(u'\xbf',"")
            queryColumns+="%s," % key
            if(rrevent[key]!='NULL'): queryValues+="'%s'," % rrevent[key]
            else: queryValues+="NULL,"

        queryColumns += "lonlat)"
        
        query_archive = "INSERT INTO archive" + queryColumns + queryValues + geoValue
        # Insert tfl event into archive
        cursor.execute(query_archive)

        query_tfl = "INSERT INTO tfl" + queryColumns + queryValues + geoValue
        # Insert tfl event into the table with the current events
        cursor.execute(query_tfl)
        return
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Insert failed! -> %s" % (exceptionValue)

###############################################################################################
######################### Executed if the script is run directly ##############################
###############################################################################################
        
if __name__ == "__main__":
    # Read the database and tfl values from a file
    Config = ConfigParser.ConfigParser()
    Config.read("../../t4t_credentials.txt")
    
    configSection = "Local database"
    db = dict()
    db['user'] = Config.get(configSection, "username")
    db['password'] = Config.get(configSection, "password")
    db['database'] = Config.get(configSection, "database")
    db['host'] = Config.get(configSection, "server")

    configSection = "TfL feed"
    tfl = dict()
    tfl['email'] = Config.get(configSection, "email")
    tfl['eventfeedid'] = Config.get(configSection, "eventfeedid")

    # Parse the command line arguments
    parser=optparse.OptionParser()
    parser.add_option('-v','--verbosity',
            dest='verbosity',
            default=0,
            help='Set the verbosity',
            type=int)
    (options, args)=parser.parse_args()

    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    
    sampleFeed()

###############################################################################################
############################ Executed if the script is imported ###############################
###############################################################################################

else:
    db = dict()
    tfl = dict()
    kwargs = dict()

def startThread():
    # Create a new thread
    thread.start_new_thread(sampleFeed, ())
