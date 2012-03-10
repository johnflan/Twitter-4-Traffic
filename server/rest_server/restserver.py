from flask import Flask, request, send_file
import sys
import optparse
import ConfigParser
from pg8000 import DBAPI
import json
import thread
from datetime import datetime

app = Flask(__name__)

response_data = {'test.html': None}

###############################################################################################
######################### Server requests used for the test webpage ###########################
###############################################################################################
                    
@app.route("/", methods=['GET'])
def instructions():
    return getResponse('test.html')

@app.route("/favicon.ico")
def get_favicon():
    return send_file('responses/images/favicon.ico',mimetype='image/x-icon')
    
@app.route("/header_bg.png")
def get_header():
    return send_file('responses/images/header_bg.png',mimetype='image/png')

################################## Get responses from files ###################################
def getResponse(endpoint):
    response = response_data[endpoint]
    # If the file is loaded
    if not response == None:
        return response
    else:
        return "Error no data found"

################################## Load responses from files ##################################    
def loadResponseData(respDir):
    iterFilesList = response_data.copy()
    for fileName in iterFilesList:
        try:
            f = open(respDir+'/'+fileName, 'r')
            response_data[fileName] = f.read()
        except IOError:
            print "Error unable to open: ", fileName
            
###############################################################################################
############################# VERSION 0.2 Requests for the server #############################
###############################################################################################

########################## Get disruptions in a circle or rectangle ###########################
@app.route("/t4t/0.2/disruptions", methods=['GET'])
def disruptions02():
    
    closestcam = "n"
    # If closestcam is y then only one will be returned for each event
    if ( 'closestcam' in request.args ):
        if request.args['closestcam'] == "y":
            closestcam = "y"
    
    # Disruptions within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid disruptions request:"
        response=app.make_response(findDisruptionsRadius(request.args['longitude'], 
                               request.args['latitude'],
                               request.args['radius'], closestcam))
        response.mimetype='application/json'
        return response
    # Disruptions within a rectangle
    if ('topleftlat' in request.args and 'topleftlong' in request.args and
        'bottomrightlat' in request.args and 'bottomrightlong' in
        request.args):
        print "[INFO] Valid disruptions request"
        response=app.make_response(findDisruptionsRect(request.args['topleftlong'], 
                               request.args['topleftlat'],
                               request.args['bottomrightlong'],
                               request.args['bottomrightlat'], closestcam))
        response.mimetype='application/json'
        return response

    return "Invalid disruptions request", 400

################################ Get disruptions around a route ###############################
@app.route("/t4t/0.2/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute02():
    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.json
        points = getPointsFromJson(str(request.json))
        response=app.make_response(findDisruptionsRoute(points,"n",1000))
        response.mimetype='application/json'
        return response
    return "Invalid request", 400

######################################### Get tweets ##########################################
@app.route("/t4t/0.2/tweets", methods=['GET'])
def tweets02():
    proffilter="n"
    # Find the profanity filter value
    if ('filter' in request.args):
        if (request.args['filter']=='y'):
            proffilter = "y"

    # Get tweets around a disruption
    if ('disruptionID' in request.args):
        print "[INFO] Valid tweets request"
        response=app.make_response(findTweetsDisruption(request.args['disruptionID'], proffilter))
        response.mimetype='application/json'
        return response
    
    # Get tweets within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid tweets request"
        response=app.make_response(findTweetsRadius(request.args['longitude'],
                                                    request.args['latitude'],
                                                    request.args['radius'],
                                                    proffilter))
        response.mimetype='application/json'
        return response
    return "Invalid tweets request", 400

################################## Get traffic cameras ########################################
@app.route("/t4t/0.2/cameras", methods=['GET'])
def cameras02():
    # Get cameras around a disruption
    if ('disruptionID' in request.args):
        print "[INFO] Valid cameras request"
        if ('closestcam' in request.args):
            if request.args['closestcam']=="y":
                response=app.make_response(findCamerasDisruptionClosest(request.args['disruptionID']))
                response.mimetype='application/json'
                return response
        else:
            response=app.make_response(findCamerasDisruption(request.args['disruptionID']))
            response.mimetype='application/json'
            return response
    
    # Get cameras within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid cameras request"
        response=app.make_response(findCamerasRadius(request.args['longitude'], 
                               request.args['latitude'],
                               request.args['radius']))
        response.mimetype='application/json'
        return response
    return "Invalid cameras request", 400

######################################## Report event #########################################
@app.route("/t4t/0.2/report", methods=['PUT', 'POST'])
def report02():
    if (request.mimetype == "application/json"):
        print "[INFO] received json body, ", request.json
        return "Success"
    return "Invalid request", 400

###############################################################################################
################################## Starts the rest server #####################################
###############################################################################################

def startServer():
    # Connect to the database
    connect()
    # Load responses from files for the mock server and the test webpage
    loadResponseData(kwargs['resp'])
    # Start the server
    app.run(host=kwargs['server'],port=kwargs['port'])

###############################################################################################
################################ Connects to the database #####################################
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
############# Returns a JSON text for the rectangular area that is selected ###################
###############################################################################################
        
def findDisruptionsRect(lonTL, latTL, lonBR, latBR, closestcam):
    try:
        rectangle = "%s %s, %s %s, %s %s, %s %s, %s %s" % (lonTL,latTL, lonTL,latBR, lonBR,latBR, lonBR,latTL, lonTL,latTL)
        query = """SELECT updated_at,
                            ltisid, 
                            eventstartdate,
                            eventstarttime,
                            eventenddate,
                            eventendtime,
                            event_type,
                            category,
                            title,
                            sector,
                            location,
                            description,
                            lastmodifiedtime,
                            severity,
                            postcodestart,
                            postcodeend,
                            remarkdate,
                            remarktime,
                            remark,
                            grideasting,
                            gridnorthing,
                            ST_AsText(lonlat)
                    FROM tfl 
                    WHERE ST_Covers(ST_GeometryFromText('POLYGON((%s))', 4326), lonlat)""" % rectangle

        cursor.execute(query)
        disruptionRows = cursor.fetchall()
        
        jsonText = disruptionRows2JSON(disruptionRows, closestcam)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)
        return "Invalid disruptions request", 400

###############################################################################################
#################### Returns a JSON text for the area that is selected ########################
###############################################################################################
        
def findDisruptionsRadius(lon, lat, radius, closestcam):
    try:
        query = """SELECT updated_at,
                            ltisid, 
                            eventstartdate,
                            eventstarttime,
                            eventenddate,
                            eventendtime,
                            event_type,
                            category,
                            title,
                            sector,
                            location,
                            description,
                            lastmodifiedtime,
                            severity,
                            postcodestart,
                            postcodeend,
                            remarkdate,
                            remarktime,
                            remark,
                            grideasting,
                            gridnorthing,
                            ST_AsText(lonlat)
                    FROM tfl 
                    WHERE ST_DWithin(lonlat,'POINT(%s %s)', %s)""" % (lon,lat,radius)

        cursor.execute(query)
        disruptionRows = cursor.fetchall()
        
        jsonText = disruptionRows2JSON(disruptionRows, closestcam)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)
        return "Invalid disruptions request", 400

###############################################################################################
########################## Returns route points from a JSON file ##############################
###############################################################################################
        
def getPointsFromJson(json_data):
    json_data = json_data.replace("u'","\"").replace("'","\"")
    data = json.loads(json_data)
    return data["points"]
    
###############################################################################################
#################### Returns a JSON text for the area that is selected ########################
###############################################################################################
        
def findDisruptionsRoute(points, closestcam, radius=1000):
    try:
        route = "LINESTRING("
        for point in points:
            route += "%s %s," % (point['lon'], point['lat'])
        route = route[:-1]+")"

        query = """SELECT updated_at,
                            ltisid, 
                            eventstartdate,
                            eventstarttime,
                            eventenddate,
                            eventendtime,
                            event_type,
                            category,
                            title,
                            sector,
                            location,
                            description,
                            lastmodifiedtime,
                            severity,
                            postcodestart,
                            postcodeend,
                            remarkdate,
                            remarktime,
                            remark,
                            ST_AsText(lonlat)
                    FROM tfl 
                    WHERE ST_DWithin(lonlat,'%s', %s)""" % (route,radius)
        
        cursor.execute(query)
        disruptionRows = cursor.fetchall()
        
        jsonText = disruptionRows2JSON(disruptionRows, closestcam)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)       

###############################################################################################
###################### Returns a JSON text for the rows of the table ##########################
###############################################################################################
        
def disruptionRows2JSON(disruptionRows, closestcam):
    jsonRow = ""
    for row in disruptionRows:
        coordinates = row[-1][6:-1]
        lonlatArray = coordinates.split(" ")
        longitude = lonlatArray[0]
        latitude = lonlatArray[1]
        jsonRow += """    {
        \"updated_at\": \"%s\",
        \"ltisid\": \"%s\",
        \"eventstartdate\": \"%s\",
        \"eventstarttime\": \"%s\",
        \"eventenddate\": \"%s\",
        \"eventendtime\": \"%s\",
        \"event_type\": \"%s\",
        \"category\": \"%s\",
        \"title\": \"%s\",
        \"sector\": \"%s\",
        \"location\": \"%s\",
        \"description\": \"%s\",
        \"lastmodifiedtime\": \"%s\",
        \"severity\": \"%s\",
        \"postcodestart\": \"%s\",
        \"postcodeend\": \"%s\",
        \"remarkdate\": \"%s\",
        \"remarktime\": \"%s\",
        \"remark\": \"%s\",
        \"longitude\": \"%s\",
        \"latitude\": \"%s\",
        """ % (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],
                row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],
                longitude, latitude)
        
        if closestcam=="y":
            cameras = findCamerasDisruptionClosest(row[1])
        elif closestcam=="n":
            cameras = findCamerasDisruption(row[1])
        
        jsonRow += "    " + cameras[1:-1]
        jsonRow +="""\n    },\n"""
        
    
    jsonText = "{\"disruptions\":[\n%s\n]}" % jsonRow[:-2]
    return jsonText

###############################################################################################
#################### Returns a JSON text for the area that is selected ########################
###############################################################################################

def findTweetsRadius(lon, lat, radius, proffilter):
    try:
        # Filter profanities
        queryForFilter = ""
        if proffilter=="y":
            queryForFilter = " WHERE profanity='n'"
            
        query = """SELECT tid, uname, rname, created_at, location, text, probability, st_distance, geolocation FROM (SELECT tid,
                            uname,
                            rname,
                            created_at,
                            location,
                            text,
                            probability,
                            ST_Distance(geolocation,'POINT(%s %s)') AS st_distance,
                            ST_AsText(geolocation) as geolocation
                    FROM tweets%s) AS distances
                    WHERE st_distance <= %s""" % (lon,lat,queryForFilter,radius)

        cursor.execute(query)
        tweetRows = cursor.fetchall()
                
        jsonText = tweetRows2JSON(tweetRows, radius)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)
        
###############################################################################################
################## Returns a JSON text for the area around a disruption #######################
###############################################################################################

def findTweetsDisruption(ltisid, proffilter, radius=1000):
    try:
        # Filter profanities
        queryForFilter = ""
        if proffilter=="y":
            queryForFilter = " WHERE profanity='n'"
            
        query = """SELECT tid, uname, rname, created_at, location, text, probability, st_distance, geolocation FROM (SELECT tid,
                            uname,
                            rname,
                            created_at,
                            location,
                            text,
                            probability,
                            ST_Distance(geolocation,(SELECT lonlat FROM tfl WHERE ltisid=%s)) AS st_distance,
                            ST_AsText(geolocation) as geolocation
                    FROM tweets%s) AS distances
                    WHERE st_distance <= %s""" % (ltisid,queryForFilter,radius)

        cursor.execute(query)
        tweetRows = cursor.fetchall()
                
        jsonText = tweetRows2JSON(tweetRows, radius)      
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)

###############################################################################################
##################### Returns a JSON text for the rows of the table ###########################
###############################################################################################
        
def tweetRows2JSON(tweetRows, radius):
    jsonRow = ""
    for row in tweetRows:
        ranking=calculateRank(float(row[6]), float(row[7]), float(radius), row[3]);
        coordinates = row[-1][6:-1]
        lonlatArray = coordinates.split(" ")
        longitude = lonlatArray[0]
        latitude = lonlatArray[1]

        jsonRow += """    {
        \"tid\": \"%s\",
        \"uname\": \"%s\",
        \"rname\": \"%s\",
        \"created_at\": \"%s\",
        \"location\": \"%s\",
        \"text\": \"%s\",
        \"longitude\": \"%s\",
        \"latitude\": \"%s\",
                \"ranking\": \"%s\"
    },\n""" % (row[0],row[1],row[2],row[3],row[4].replace('"',"'"),row[5].replace('"',"'"),longitude,latitude,ranking)
    
    jsonText = "{\"tweets\":[\n%s\n]}" % jsonRow[:-2]
    return jsonText.encode()

###############################################################################################
################################ Calculate the rank of the tweet ##############################
###############################################################################################
    
def calculateRank(prob, distance, radius, created_at):
    # Max age of the life of each tweet is 36 hours (129600 sec)
    max_age = 129600
    # Find the age of the tweet
    tweets_age = (datetime.now() - created_at).seconds
    # The rank depends on the distance of the tweet to the event
    # on the probability of being about traffic
    # and on its age.

    tweetRank = 0.3 * (radius-distance)/radius + 0.4 * prob + 0.3 * (max_age - tweets_age) / max_age;
    return tweetRank    
    
###############################################################################################
#################### Returns a JSON text for the area that is selected ########################
###############################################################################################

def findCamerasRadius(lon, lat, radius):
    try:
        query = """SELECT title,
                            link,
                            ST_AsText(geolocation)
                    FROM cameras
                    WHERE ST_DWithin(geolocation,'POINT(%s %s)', %s)""" % (lon,lat,radius)

        cursor.execute(query)
        cameraRows = cursor.fetchall()
        
        jsonText = cameraRows2JSON(cameraRows)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)
        
###############################################################################################
################## Returns a JSON text for the area around a disruption #######################
###############################################################################################

def findCamerasDisruption(ltisid, radius=500):
    try:
        query = """SELECT title,
                            link,
                            ST_AsText(geolocation)
                    FROM cameras
                    WHERE ST_DWithin(geolocation,(SELECT lonlat FROM tfl WHERE ltisid=%s), %s)""" % (ltisid,radius)

        cursor.execute(query)
        cameraRows = cursor.fetchall()
        
        jsonText = cameraRows2JSON(cameraRows)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)

###############################################################################################
############## Returns a JSON text for the closest camera around a disruption #################
###############################################################################################

def findCamerasDisruptionClosest(ltisid, radius=500):
    try:
        query = """SELECT title, link, st_distance, geolocation
                    FROM (SELECT title,
                            link,
                            ST_Distance(geolocation,(SELECT lonlat FROM tfl WHERE ltisid=%s)) AS st_distance,
                            ST_AsText(geolocation) AS geolocation
                            FROM cameras) AS closestcam
                    WHERE st_distance<=%s 
                    ORDER BY st_distance ASC
                    LIMIT(1)""" % (ltisid,radius)
                    
        cursor.execute(query)
        cameraRows = cursor.fetchall()
        
        jsonText = cameraRows2JSON(cameraRows)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Error -> %s" % (exceptionValue)

        
###############################################################################################
##################### Returns a JSON text for the rows of the table ###########################
###############################################################################################
        
def cameraRows2JSON(cameraRows):
    jsonRow = ""
    for row in cameraRows:
        coordinates = row[-1][6:-1]
        lonlatArray = coordinates.split(" ")
        longitude = lonlatArray[0]
        latitude = lonlatArray[1]
        jsonRow += """    {
        \"title\": \"%s\",
        \"link\": \"%s\",
        \"longitude\": \"%s\",
        \"latitude\": \"%s\"
    },\n""" % (row[0],row[1],longitude,latitude)
    
    jsonText = "{\"cameras\":[\n%s\n]}" % jsonRow[:-2]
    return jsonText

###############################################################################################
######################### Executed if the script is run directly ##############################
###############################################################################################
    
if __name__ == "__main__":
    configSection="Local database"
    # Read the database values from a file
    Config = ConfigParser.ConfigParser()
    Config.read("../t4t_credentials.txt")
    
    db = dict()
    db['user'] = Config.get(configSection, "username")
    db['password'] = Config.get(configSection, "password")
    db['database'] = Config.get(configSection, "database")
    db['host'] = Config.get(configSection, "server")

    # Parse the command line arguments
    parser=optparse.OptionParser()
    parser.add_option('-p','--port',
            dest='port',
            default='55004',
            help='The server port',
            type=int)
    parser.add_option('-s', '--server',
            dest='server',
            default='0.0.0.0',
            help='The server address')
    parser.add_option('-r','--resp',
            dest='resp',
            default='/responses',
            help='The directory where the responses are saved')
    parser.add_option('-v','--verbosity',
            dest='verbosity',
            default=0,
            help='How to display information',
            type=int)
    (options, args)=parser.parse_args()
    
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])

    startServer()

###############################################################################################
############################ Executed if the script is imported ###############################
###############################################################################################

else:
    db = dict()
    kwargs = dict()

def startThread():
    # Create a new thread
    thread.start_new_thread(startServer, ())
