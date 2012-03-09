from flask import Flask, request
import sys
app = Flask(__name__)

response_data = {   'disruption_radius.txt': None,
                    'disruption_rect.txt': None,
                    'tweets_disruption_id.txt': None,
                    'tweets_radius.txt: None,
                    'cameras_disruption_id.txt': None,
                    'cameras_radius.txt: None,
                    'route_disruptions.txt':None,
                    'instructions.txt': None}

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
        return getResponse('disruptions_radius.txt')
    # Disruptions within a rectangle
    if ('topleftlat' in request.args and 'topleftlong' in request.args and
        'bottomrightlat' in request.args and 'bottomrightlong' in
        request.args):
        print "[INFO] Valid disruptions request"
        return getResponse('disruptions_rect.txt')

    return "Invalid disruptions request", 400

################################ Get disruptions around a route ###############################
@app.route("/t4t/0.2/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute02():
    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.json
        return getResponse('route_disruptions.txt')
    return "Invalid request", 400

######################################### Get tweets ##########################################
@app.route("/t4t/0.2/tweets", methods=['GET'])
def tweets02():
    # Get tweets around a disruption
    if ('disruptionID' in request.args):
        print "[INFO] Valid tweets request"
        return getResponse('tweets_disruption_id.txt')
    
    # Get tweets within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        print "[INFO] Valid tweets request"
        return getResponse('tweets_radius.txt')
    return "Invalid tweets request", 400

################################## Get traffic cameras ########################################
@app.route("/t4t/0.2/cameras", methods=['GET'])
def cameras02():
    # Get cameras around a disruption
    if ('disruptionID' in request.args):
        print "[INFO] Valid cameras request"
        if ( 'closestcam' in request.args ):
            if request['closestcam']=="y":
                return getResponse('cameras_disruption_id_closest.txt')
        return getResponse('cameras_disruption_id.txt')
    
    # Get cameras within a circle
    if ( 'radius' in request.args and 'latitude' in request.args and 'longitude'
           in request.args):
        if ( 'closestcam' in request.args ):
            if request['closestcam']=="y":
                return getResponse('cameras_radius_closest.txt')
        return getResponse('cameras_radius.txt')
    return "Invalid cameras request", 400

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
