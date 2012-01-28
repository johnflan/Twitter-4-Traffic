from flask import Flask, request
import sys
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

    return "Invalid disruptions request", 500

#POST is for creating
#PUT is for creating/updating
@app.route("/t4t/0.1/disruptions/route/", methods=['PUT','POST'])
def disruptionsRoute():

    if request.mimetype == "application/json":
        print"[INFO] recieved json body:", request.data
        return getResponse('route_disruptions.txt')
    
    return "Invalid request", 500

@app.route("/t4t/0.1/tweets", methods=['GET'])
def tweets():
    if ('disruptionID' in request.args):
        return getResponse('tweets_disruption_id.txt')

    return "Invalid tweet request", 500


@app.route("/t4t/0.1/report", methods=['PUT', 'POST'])
def report():
    if (request.mimetype == "application/json"):
        print "[INFO] received json body, ", request.data
        return "Success"
    return "Invalid request", 500

def getResponse(endpoint):
    response = response_data[endpoint]
    if not response == None:
        print response
        return response
    else:
        return "Error no data found"

def loadResponseData():
    iterFilesList = response_data.copy()
    for fileName in iterFilesList:
        try:
            f = open(fileName, 'r')
            response_data[fileName] = f.read()
        except IOError:
            print "Error unable to open: ", fileName

def main(*args,**kwargs):
    loadResponseData()
    app.run(host=kwargs['server'],port=kwargs['port'])

if __name__ == "__main__":
    from optparse import OptionParser
    parser=OptionParser()
    parser.add_option('-s', '--server',
            dest='server',
            default='0.0.0.0',
            help='The server address')
    parser.add_option('-p','--port',
            dest='port',
            default='55003',
            help='The server port',
            type=int)
    parser.add_option('-r','--resp',
            dest='resp',
            default='/responses',
            help='The directory where the responses are saved')
    (options, args)=parser.parse_args()
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    main(*args,**kwargs)

