from flask import Flask, request
import sys
import optparse
import ConfigParser
from pg8000 import DBAPI
import json

app = Flask(__name__)

response_data = {   'disruption_radius.txt': None,
                    'disruption_rect.txt': None,
                    'tweets_disruption_id.txt': None,
                    'route_disruptions.txt':None,
                    'instructions.txt': None}

@app.route("/", methods=['GET'])
def instructions():
    return getResponse('instructions.txt')

#--- API V0.1 ----------------------------------------------------

@app.route("/t4t/0.1/disruptions", methods=['GET'])
def disruptions():
    
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid disruptions request:"
        print "\tRadius: ", request.args['radius'], ", Latitude: ",\
            request.args['latitude'], ", Longitude: ",\
            request.args['longitude']
        return getResponse('disruption_radius.txt')

    if ('topleftlat' in request.args and 'topleftlong' in request.args and
        'bottomrightlat' in request.args and 'bottomrightlong' in
        request.args):
        print "[INFO] Valid disruptions request"
        print "\tTop left latitude: ", request.args['topleftlat'], \
                ", top left longitude: ", request.args['topleftlong'],\
                ", Bottom right latitude: ", request.args['bottomrightlat'],\
                ", bottom right longitude: ", request.args['bottomrightlong']
        return getResponse('disruption_rect.txt')

    return "Invalid disruptions request", 400

#POST is for creating
#PUT is for creating/updating
@app.route("/t4t/0.1/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute():
    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.json
        return getResponse('route_disruptions.txt')
    return "Invalid request", 400

@app.route("/t4t/0.1/tweets", methods=['GET'])
def tweets():
    if ('disruptionID' in request.args):
        return getResponse('tweets_disruption_id.txt')
    return "Invalid tweet request", 400


@app.route("/t4t/0.1/report", methods=['PUT', 'POST'])
def report():
    if (request.mimetype == "application/json"):
        print "[INFO] received json body, ", request.json
        return "Success"
    return "Invalid request", 400

def getResponse(endpoint):
    response = response_data[endpoint]
    if not response == None:
        print response
        return response
    else:
        return "Error no data found"

def loadResponseData(respDir):
    iterFilesList = response_data.copy()
    for fileName in iterFilesList:
        try:
            f = open(respDir+'/'+fileName, 'r')
            response_data[fileName] = f.read()
        except IOError:
            print "Error unable to open: ", fileName
            
#--- API V0.2 ----------------------------------------------------

@app.route("/t4t/0.2/disruptions", methods=['GET'])
def disruptions():
    
    closestcam = "n"
    if ( 'closestcam' in request.args ):
        if request.args['closestcam'] == "y":
            closestcam = "y"
    
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid disruptions request:"
        print "\tRadius: ", request.args['radius'], ", Latitude: ",\
            request.args['latitude'], ", Longitude: ",\
            request.args['longitude']
            
        return findDisruptionsRadius(request.args['longitude'], 
                               request.args['latitude'],
                               request.args['radius'], closestcam)

    if ('topleftlat' in request.args and 'topleftlong' in request.args and
        'bottomrightlat' in request.args and 'bottomrightlong' in
        request.args):
        print "[INFO] Valid disruptions request"
        print "\tTop left latitude: ", request.args['topleftlat'], \
                ", top left longitude: ", request.args['topleftlong'],\
                ", Bottom right latitude: ", request.args['bottomrightlat'],\
                ", bottom right longitude: ", request.args['bottomrightlong']
    return findDisruptionsRect(request.args['topleftlong'], 
                               request.args['topleftlat'],
                               request.args['bottomrightlong'],
                               request.args['bottomrightlat'], closestcam)

    return "Invalid disruptions request", 400

#POST is for creating
#PUT is for creating/updating
@app.route("/t4t/0.2/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute():
    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.json
        points = getPointsFromJson(str(request.json))
        return findDisruptionsRoute(points,"n",1000)
    return "Invalid request", 400

@app.route("/t4t/0.2/tweets", methods=['GET'])
def tweets():
    if ('disruptionID' in request.args):
        print "[INFO] Valid tweets request"
        return findTweetsDisruption(request.args['disruptionID'])
    
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid tweets request"
        return findTweetsRadius(request.args['longitude'], 
                               request.args['latitude'],
                               request.args['radius'])
        
    return "Invalid tweets request", 400

@app.route("/t4t/0.2/cameras", methods=['GET'])
def cameras():
    if ('disruptionID' in request.args):
        print "[INFO] Valid cameras request"
        if ('closestcam' in request.args):
            if request.args['closestcam']=="y":
                return findCamerasDisruptionClosest(request.args['disruptionID'])
        else:
            return findCamerasDisruption(request.args['disruptionID'])
    
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid cameras request"
        return findCamerasRadius(request.args['longitude'], 
                               request.args['latitude'],
                               request.args['radius'])
        
    return "Invalid cameras request", 400
    
@app.route("/t4t/0.2/report", methods=['PUT', 'POST'])
def report():
    if (request.mimetype == "application/json"):
        print "[INFO] received json body, ", request.json
        return "Success"
    return "Invalid request", 400

def getResponse(endpoint):
    response = response_data[endpoint]
    if not response == None:
        print response
        return response
    else:
        return "Error no data found"

def loadResponseData(respDir):
    iterFilesList = response_data.copy()
    for fileName in iterFilesList:
        try:
            f = open(respDir+'/'+fileName, 'r')
            response_data[fileName] = f.read()
        except IOError:
            print "Error unable to open: ", fileName

def main(*args,**kwargs):
    loadResponseData(kwargs['resp'])
    app.run(host=kwargs['server'],port=kwargs['port'])

###############################################################################################
################################ Connects to the database #####################################
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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))

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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))

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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))        

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

def findTweetsRadius(lon, lat, radius):
    try:
        query = """SELECT tid,
                            uname,
                            created_at,
                            location,
                            text,
                            probability,
                            ST_AsText(geolocation)
                    FROM tweets
                    WHERE ST_DWithin(geolocation,'POINT(%s %s)', %s)""" % (lon,lat,radius)

        cursor.execute(query)
        tweetRows = cursor.fetchall()
				
        jsonText = tweetRows2JSON(tweetRows,lon,lat)
        
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))
        
###############################################################################################
################## Returns a JSON text for the area around a disruption #######################
###############################################################################################

def findTweetsDisruption(ltisid, radius=1000):
    try:
        
        query = """SELECT tid,
                            uname,
                            created_at,
                            location,
                            text,
                            probability,
                            ST_AsText(geolocation)
                    FROM tweets
                    WHERE ST_DWithin(geolocation,(SELECT lonlat FROM tfl WHERE ltisid=%s), %s)""" % (ltisid,radius)

        cursor.execute(query)
        tweetRows = cursor.fetchall()
				
				#Calculate lon, lat from the disruption ID
        query = "SELECT ST_AsText(lonlat) FROM tfl WHERE ltisid="+ltisid
        cursor.execute(query)
        lonlat = cursor.fetchone()
        coordinates = lonlat[-1][6:-1]
        lonlatArray = coordinates.split(" ")
        lon = lonlatArray[0]
        lat = lonlatArray[1]	
				
        jsonText = tweetRows2JSON(tweetRows,lon,lat)      
        return jsonText        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))

###############################################################################################
##################### Returns a JSON text for the rows of the table ###########################
###############################################################################################
def calculateRank(tid, lon, lat, prob):
    query = """select ST_Distance('POINT(%s %s)',( select geolocation from tweets where tid=%s))""" % (lon, lat, tid);
    cursor.execute(query);
    tweetDistance=cursor.fetchone()
    tweetDistance=float(tweetDistance[0])
    if tweetDistance==0:
        tweetDistance=1
    tweetRank=0.6*(1/tweetDistance)+0.4*float(prob);
    return tweetRank
		
def tweetRows2JSON(tweetRows,lon,lat):
    jsonRow = ""
    for row in tweetRows:
        ranking=calculateRank(row[0],lon,lat,row[5]);
        coordinates = row[-1][6:-1]
        lonlatArray = coordinates.split(" ")
        longitude = lonlatArray[0]
        latitude = lonlatArray[1]
        jsonRow += """    {
        \"tid\": \"%s\",
        \"uname\": \"%s\",
        \"created_at\": \"%s\",
        \"location\": \"%s\",
        \"text\": \"%s\",
        \"longitude\": \"%s\",
        \"latitude\": \"%s\",
				\"ranking\": \"%s\"
    },\n""" % (row[0],row[1],row[2],row[3],row[4],longitude,latitude,ranking)
    
    jsonText = "{\"tweets\":[\n%s\n]}" % jsonRow[:-2]
    return jsonText

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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))
        
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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))

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
        # Exit the script and print an error telling what happened.
        sys.exit("Database select failed! -> %s" % (exceptionValue))

        
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

if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("../t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")

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
    parser.add_option('-H','--host',
            dest='host',
            default=host,
            help='The hostname of the DB')
    parser.add_option('-d','--database',
            dest='database',
            default=database,
            help='The name of the DB')
    parser.add_option('-U','--user',
            dest='user',
            default=user,
            help='The username for the DB')
    parser.add_option('-P','--password',
            dest='password',
            default=password,
            help='The password for the DB')
    (options, args)=parser.parse_args()
    
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    db = dict([[k,v] for k,v in kwargs.iteritems() if k!='port' and k!='resp' and k!='server'])        
    cursor, conn = connect(**db)
    main(*args,**kwargs)
