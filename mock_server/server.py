from flask import Flask, request, send_file
import sys
import optparse
app = Flask(__name__)


response_data = {   'disruption_radius.txt': None,
                    'disruption_rect.txt': None,
                    'tweets_disruption_id.txt': None,
                    'tweets_radius.txt': None,
                    'cameras_disruption_id.txt': None,
                    'cameras_radius.txt': None,
                    'cameras_disruption_id_closest.txt': None,
                    'cameras_radius_closest.txt': None,
                    'route_disruptions.txt':None,
                    'instructions.txt': None,
                    'test.html': None}

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
        radius=is_number(request.args['radius'])
        latitude=is_number(request.args['latitude'])
        longitude=is_number(request.args['longitude'])
        if (radius!=None and latitude!=None and longitude!=None):
            if (radius>=0 and abs(latitude)<=90 and abs(longitude)<=180):
                print "[INFO] Valid disruptions request:"
            else:
                return "Invalid disruptions request", 400
        else:
            return "Invalid disruptions request", 400
        response=app.make_response(getResponse('disruption_radius.txt'))
        response.mimetype='application/json'
        return response
    # Disruptions within a rectangle
    if ('topleftlat' in request.args and 'topleftlong' in request.args and
        'bottomrightlat' in request.args and 'bottomrightlong' in
        request.args):
        topleftlat=is_number(request.args['topleftlat'])
        topleftlong=is_number(request.args['topleftlong'])
        bottomrightlat=is_number(request.args['bottomrightlat'])
        bottomrightlong=is_number(request.args['bottomrightlong'])
        if (topleftlat!=None and topleftlong!=None and bottomrightlat!=None and
                bottomrightlong!=None):
            if (abs(topleftlat)<=90 
                    and abs(topleftlong)<=180
                    and abs(bottomrightlat)<=90
                    and abs(bottomrightlong)<=180):
                print "[INFO] Valid disruptions request:"
            else:
                return "Invalid disruptions request", 400
        else:
            return "Invalid disruptions request", 400
        response=app.make_response(getResponse('disruption_rect.txt'))
        response.mimetype='application/json'
        return response
    return "Invalid disruptions request", 400

################################ Get disruptions around a route ###############################
@app.route("/t4t/0.2/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute02():
    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.json
        response=app.make_response(getResponse('route_disruptions.txt'))
        response.mimetype='application/json'
        return response
    return "Invalid request", 400

######################################### Get tweets ##########################################
@app.route("/t4t/0.2/tweets", methods=['GET'])
def tweets02():
    # Get tweets around a disruption
    if ('disruptionID' in request.args):
        disruptionID=is_int(request.args['disruptionID'])
        if (disruptionID!=None):
            if (disruptionID>=0):
                print "[INFO] Valid tweets request:"
            else:
                return "Invalid tweets request", 400
        else:
            return "Invalid tweets request", 400
        response=app.make_response(getResponse('tweets_disruption_id.txt'))
        response.mimetype='application/json'
        return response
    
    # Get tweets within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        radius=is_number(request.args['radius'])
        latitude=is_number(request.args['latitude'])
        longitude=is_number(request.args['longitude'])
        if (radius!=None and latitude!=None and longitude!=None):
            if (radius>=0 and abs(latitude)<=90 and abs(longitude)<=180):
                print "[INFO] Valid tweets request:"
            else:
                return "Invalid tweets request", 400
        else:
            return "Invalid tweets request", 400
        response=app.make_response(getResponse('tweets_radius.txt'))
        response.mimetype='application/json'
        return response
    return "Invalid tweets request", 400

################################## Get traffic cameras ########################################
@app.route("/t4t/0.2/cameras", methods=['GET'])
def cameras02():
    # Get cameras around a disruption
    if ('disruptionID' in request.args):
        disruptionID=is_int(request.args['disruptionID'])
        if (disruptionID!=None):
            if (disruptionID>=0):
                print "[INFO] Valid cameras request:"
            else:
                return "Invalid cameras request", 400
        else:
            return "Invalid cameras request", 400
        if ( 'closestcam' in request.args ):
            if request.args['closestcam']=="y":
                response=app.make_response(getResponse('cameras_disruption_id_closest.txt'))
                response.mimetype='application/json'
                return response
        response=app.make_response(getResponse('cameras_disruption_id.txt'))
        response.mimetype='application/json'
        return response
    
    # Get cameras within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        radius=is_number(request.args['radius'])
        latitude=is_number(request.args['latitude'])
        longitude=is_number(request.args['longitude'])
        if (radius!=None and latitude!=None and longitude!=None):
            if (radius>=0 and abs(latitude)<=90 and abs(longitude)<=180):
                print "[INFO] Valid cameras request:"
            else:
                return "Invalid cameras request", 400
        else:
            return "Invalid cameras request", 400
        if ( 'closestcam' in request.args ):
            if request.args['closestcam']=="y":
                response=app.make_response(getResponse('cameras_radius_closest.txt'))
                response.mimetype='application/json'
                return response
        response=app.make_response(getResponse('cameras_radius.txt'))
        response.mimetype='application/json'
        return response
    return "Invalid cameras request", 400
		
################################## Check if float #############################################
def is_number(s):
    try:
        return float(s) # for int, long and float
    except ValueError:
        return None
################################## Check if integer ###########################################
def is_int(s):
    try:
        return int(s) # for int, long and float
    except ValueError:
        return None
				
###############################################################################################
################################## Starts the rest server #####################################
###############################################################################################

def startServer():
    # Load responses from files for the mock server and the test webpage
    loadResponseData(kwargs['resp'])
    # Start the server
    app.run(host=kwargs['server'],port=kwargs['port'])

###############################################################################################
######################### Executed if the script is run directly ##############################
###############################################################################################
    
if __name__ == "__main__":
    # Parse the command line arguments
    parser=optparse.OptionParser()
    parser.add_option('-p','--port',
            dest='port',
            default='55003',
            help='The mock server port',
            type=int)
    parser.add_option('-s', '--server',
            dest='server',
            default='0.0.0.0',
            help='The mock server address')
    parser.add_option('-r','--resp',
            dest='resp',
            default='responses/',
            help='The directory where the responses are saved')
    parser.add_option('-v','--verbosity',
            dest='verbosity',
            default=0,
            help='How to display information',
            type=int)
    (options, args)=parser.parse_args()
    
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])

    startServer()
