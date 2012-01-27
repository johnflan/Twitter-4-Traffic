from flask import Flask
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

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=55003)
