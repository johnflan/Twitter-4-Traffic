from flask import Flask
import sys
app = Flask(__name__)

response_data = {   'disruption_radius.txt': None,
                    'disruption_rect.txt': None,
                    'tweets_disruption_id.txt': None,
                    'instructions.txt': None}

@app.route("/")
def hello():
    return getResponse('instructions.txt')

#--- API V0.1 ----------------------------------------------------
@app.route("/0.1/disruptions/")
def disruptions():
        return getResponse('disruptions_rect.txt') 


@app.route("/0.1/disruptions/route/")
def disruptionsRoute():
        return "Hello World!"


@app.route("/0.1/tweets/")
def tweets():
        return "Hello World!"


@app.route("/0.1/report/")
def report():
        return "Hello World!"

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

