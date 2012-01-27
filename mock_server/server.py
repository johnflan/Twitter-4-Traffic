from flask import Flask
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

def loadResponseData():
    iterFilesList = response_data.copy()
    for fileName in iterFilesList:
        try:
            f = open(fileName, 'r')
            response_data[fileName] = f.read()
        except IOError:
            print "Error unable to open: ", fileName

if __name__ == "__main__":
    loadResponseData()
    app.run(host='0.0.0.0',port=55003)
