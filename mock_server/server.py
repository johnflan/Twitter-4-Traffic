from flask import Flask
import sys
app = Flask(__name__)


#(GET) /t4t/0.1/disruptions/?lat=xxx&long=xxx&radius=xxx
#(GET) /t4t/0.1/disruptions/?topleft=xxx,xxx&bottomright=xxx,xxx
#(POST) /t4t/0.1/disruptions/route/
#(GET) /t4t/0.1/tweets/?disruptionID=xxx
#(PUT) /t4t/0.1/report/

response_data = {   'disruption_radius.txt': None,
                    'disruption_rect.txt': None,
                    'tweets_disruption_id.txt': None,
                    }


@app.route("/")
def hello():
        return """Twitter for traffic API mock server.\nThe following routes
        are available:\n\n
        (GET) /t4t/0.1/disruptions/?lat=xxx&long=xxx&radius=xxx
        (GET) /t4t/0.1/disruptions/?topleft=xxx,xxx&bottomright=xxx,xxx
        (POST) /t4t/0.1/disruptions/route/
        (GET) /t4t/0.1/tweets/?disruptionID=xxx
        (PUT) /t4t/0.1/report/
        """

#----------------------------------------------------------------
@app.route("/0.1/disruptions/")
def disruptions():
        return "Hello World!"


@app.route("/0.1/disruptions/route/")
def disruptionsRoute():
        return "Hello World!"


@app.route("/0.1/tweets/")
def tweets():
        return "Hello World!"


@app.route("/0.1/report/")
def report():
        return "Hello World!"

def main(*args,**kwargs):
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


