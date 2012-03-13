from pg8000 import DBAPI
from xml.dom.minidom import parseString
import sys
import optparse
import ConfigParser
import time
from time import strftime
import urllib2
import thread
import logging

###############################################################################################
###################### Create a new logger to store messages in a file ########################
###############################################################################################

def createLogger():
    global logger
    logger = logging.getLogger('CameraLogger')
    logger.setLevel(kwargs['verbosity'])
    ch = logging.FileHandler(kwargs['tflcameraslog'])
    ch.setLevel(kwargs['verbosity'])
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

###############################################################################################
################### Display an error message and store it in the log file #####################
###############################################################################################

def errorMessage(errorMsg):
    logger.error(errorMsg)
    print errorMsg

###############################################################################################
#################### Display an info message and store it in the log file #####################
###############################################################################################

def infoMessage(infoMsg):
    logger.info(infoMsg)
    print infoMsg

###############################################################################################
############################ Creates a connection to the db ###################################
###############################################################################################

def connect():
    logger.debug('Connecting to the database')
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
        errorMessage("Database connection failed! -> %s" % (exceptionValue))
        sys.exit()
    logger.debug('Connected to the database')

###############################################################################################
############################# Loads a camera feed from tfl ####################################
###############################################################################################

def sampleFeed():
    # Create a log file
    createLogger()

    # Connect to the database
    connect()

    # The url for the tfl feed
    url = 'http://www.tfl.gov.uk/tfl/businessandpartners/syndication/feed.aspx?email=%s&feedid=%s' % (tfl['email'], tfl['camfeedid'])
    refresh = 300
    while True:
        try:
            logger.debug('Starting to get a new tfl feed')
            tStart = time.time()
            # Get the current time
            updated_at = strftime("%d/%m/%y %H:%M:%S")

            # Get the dom object
            req = urllib2.Request(url)
            data = urllib2.urlopen(req).read()
            dom = parseString(data.encode("ascii", "ignore"))

            # Store the dom object in the database
            storeTflData(dom)
            
            tEnd = time.time()
            # Find the time that remains until the next update
            remain = refresh - ( tEnd - tStart )
            infoMessage("TfL Camera Feed Stored @%s" % updated_at)
            infoMessage("Sleeping For %s Seconds" % remain)
            if remain > 0: time.sleep(remain)
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            errorMessage("Error in sampleFeed -> %s" % (exceptionValue))
            time.sleep(refresh)

###############################################################################################
########################### Store the tfl feed in the database ################################
###############################################################################################

def storeTflData(dom):
    cameras = dom.getElementsByTagName('rss')[0].getElementsByTagName('channel')[0].getElementsByTagName('item')
    try:
        # Delete previous data from the table
        cursor.execute("DELETE FROM cameras")    

    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        errorMessage("Delete failed in storeTfLData -> %s" % (exceptionValue))

    try:
        # For every tfl camera find each element
        for camera in cameras:
            cam = {}
            cam['title'] = camera.getElementsByTagName("title")[0].firstChild.data
            cam['link'] = camera.getElementsByTagName("link")[0].firstChild.data
            cam['description'] = camera.getElementsByTagName("description")[0].firstChild.data
            cam['geolocation'] = camera.getElementsByTagName("georss:point")[0].firstChild.data
            # Insert the tfl camera in the database
            updateCamera(**cam)

        # Commit all database changes after all cameras have been stored
        conn.commit()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        errorMessage("Commit failed in storeTfLData -> %s" % (exceptionValue))

###############################################################################################
####################### Update the cameras table of the database ##############################
###############################################################################################
    
def updateCamera(**cam):
    lat, lon = cam['geolocation'].split(' ')
    geoValue = "ST_GeographyFromText('SRID=4326; POINT(%s %s)')" % (lon, lat)
    if lat=="NaN" or lon=="NaN":
        return

    query_tfl = "INSERT INTO cameras(title,link,description,geolocation) VALUES(%s,%s,%s,"+geoValue+")"
    params = (cam['title'],cam['link'],cam['description'])

    try:
        cursor.execute(query_tfl,params)
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        errorMessage("Insert failed in updateCamera -> %s, query=%s" % (exceptionValue,query_tfl%params))

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
    tfl['camfeedid'] = Config.get(configSection, "camfeedid")

    # Parse the command line arguments
    parser=optparse.OptionParser()
    parser.add_option('-v','--verbosity',
            dest='verbosity',
            default=0,
            help='Set the verbosity',
            type=int)
    parser.add_option('--tflcameraslog',
            dest='tflcameraslog',
            default='tflcameras.log',
            help='The location for the log file')
    (options, args)=parser.parse_args()
    
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    
    logger = logging.getLogger('CameraLogger')
    logger.setLevel(kwargs['verbosity'])
    ch = logging.FileHandler(kwargs['tflcameraslog'])
    ch.setLevel(kwargs['verbosity'])
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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
    
