import optparse
import ConfigParser
import time

# Import the scripts that will be used as threads
import data_aquisition.tfl.tfl2db as tfl2db
import data_aquisition.tfl.tflcam2db as tflcam2db
import data_aquisition.twitter.tweets2db as tweets2db
import rest_server.restserver as restserver

if __name__=='__main__':
    # Read the variables from a file
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    
    configSection = "Local database"
    db = dict()
    db['user'] = Config.get(configSection, "username")
    db['password'] = Config.get(configSection, "password")
    db['database'] = Config.get(configSection, "database")
    db['host'] = Config.get(configSection, "server")

    configSection = "TfL feed"
    tfl = dict()
    tfl['email'] = Config.get(configSection, "email")
    tfl['eventfeedid'] = Config.get(configSection, "eventfeedid")
    tfl['camfeedid'] = Config.get(configSection, "camfeedid")

    parser=optparse.OptionParser()
    parser.add_option('-v','--verbosity',
            dest='verbosity',
            default=0,
            help='Set the verbosity',
            type=int)
    parser.add_option('-g',
            dest='georadius', 
            default='20.0mi', 
            help='The radius of the geocode entry for tweets')
    parser.add_option('-p','--port',
            dest='port',
            default='55004',
            help='The server port',
            type=int)
    parser.add_option('-t', '--terms',
            dest='terms',
            default='data_aquisition/twitter/searchTerms.txt',
            help='The search terms for twitter')
    parser.add_option('-w', '--words',
            dest='badwords',
            default='data_aquisition/twitter/dirty_words.txt',
            help='The bad words for the profanity filter')
    parser.add_option('-c', '--classifier',
            dest='classifier',
            default='data_aquisition/twitter/naive_bayes.pickle',
            help='The classifier file')
    parser.add_option('-s', '--server',
            dest='server',
            default='0.0.0.0',
            help='The server address')
    parser.add_option('-r','--resp',
            dest='resp',
            default='rest_server/responses',
            help='The directory where the mock server responses are saved')
    (options, args)=parser.parse_args()
    
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])

    # Start the thread that stores tfl events in the database
    tfl2db.db = db
    tfl2db.tfl = tfl
    tfl2db.kwargs = kwargs
    tfl2db.startThread()
    
    # Start the thread that stores tfl cameras in the database
    tflcam2db.db = db
    tflcam2db.tfl = tfl
    tflcam2db.kwargs = kwargs
    tflcam2db.startThread()

    # Start the thread that stores tweets in the database
    tweets2db.db = db
    tweets2db.kwargs = kwargs
    tweets2db.startThread()
    
    # Start the rest server thread
    restserver.db = db
    restserver.kwargs = kwargs
    restserver.startThread()
    
    while True:
        time.sleep(60)
