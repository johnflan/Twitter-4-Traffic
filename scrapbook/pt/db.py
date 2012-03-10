from pg8000 import DBAPI
import sys
import optparse
import ConfigParser

def main(action, *args, **db):
    # Connect to the db
    cursor, conn = connect(**db)
    
    if action=="setup":
        setup(cursor, conn, *args)
    elif action=="remove":
        rmv(cursor, conn, *args)
    elif action=="drop":
        drop(cursor, conn, *args)
    
###############################################################################################
############################ Creates a connection to the db ###################################
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
############## Creates the tables for the database if they don't exist ########################
###############################################################################################

def setup(cursor, conn, *args):
    try:
        print "> Creating tables..."
        for i in range(1,len(args)):
            if args[i]=="archive":
                cursor.execute("""CREATE TABLE archive(
                                updated_at TIMESTAMP NOT NULL,
                                ltisid INTEGER NOT NULL,
                                eventstartdate DATE,
                                eventstarttime TIME,
                                eventenddate DATE,
                                eventendtime TIME,
                                event_type TEXT,
                                category TEXT,
                                title TEXT,
                                sector TEXT,
                                location TEXT,
                                description TEXT,
                                lastmodifiedtime TIMESTAMP,
                                severity TEXT,
                                postcodestart TEXT,
                                postcodeend TEXT,
                                remarkdate DATE,
                                remarktime TIME,
                                remark TEXT,
                                grideasting DECIMAL(10,2),
                                gridnorthing DECIMAL(10,2),
                                lonlat GEOGRAPHY(POINT, 4326),
                                PRIMARY KEY (updated_at, ltisid)
                                )""")
                cursor.execute("CREATE INDEX archive_index ON tfl USING GIST (lonlat)")
                print "> Table archive created"
            elif args[i]=="tfl":                
                cursor.execute("""CREATE TABLE tfl(
                                updated_at TIMESTAMP NOT NULL,
                                ltisid INTEGER NOT NULL,
                                eventstartdate DATE,
                                eventstarttime TIME,
                                eventenddate DATE,
                                eventendtime TIME,
                                event_type TEXT,
                                category TEXT,
                                title TEXT,
                                sector TEXT,
                                location TEXT,
                                description TEXT,
                                lastmodifiedtime TIMESTAMP,
                                severity TEXT,
                                postcodestart TEXT,
                                postcodeend TEXT,
                                remarkdate DATE,
                                remarktime TIME,
                                remark TEXT,
                                grideasting DECIMAL(10,2),
                                gridnorthing DECIMAL(10,2),
                                lonlat GEOGRAPHY(POINT, 4326),
                                PRIMARY KEY (ltisid)
                                )""")
                cursor.execute("CREATE INDEX tfl_index ON tfl USING GIST (lonlat)")
                print "> Table tfl created"
            elif args[i]=="labelled_tweets":
                cursor.execute("""CREATE TABLE labelled_tweets(
                                tid BIGINT NOT NULL,
                                tweet TEXT NOT NULL,
                                ptraffic VARCHAR(1) NOT NULL,
                                ntraffic VARCHAR(1) NOT NULL,
                                unclear VARCHAR(1) NOT NULL,
                                robot VARCHAR(1) NOT NULL,
                                username VARCHAR(10) NOT NULL,
                                PRIMARY KEY (tid)
                                )""")
                print "> Table labelled_tweets created"
            elif args[i]=="static_events":
                cursor.execute("""CREATE TABLE static_events(
                                eid SERIAL NOT NULL,
                                varianceX DECIMAL,
                                meanX DECIMAL,
                                varianceY DECIMAL,
                                meanY DECIMAL,
                                PRIMARY KEY (eid)
                                )""")
                print "> Table static_events created"
            elif args[i]=="cluster_static_data":
                cursor.execute("""CREATE TABLE cluster_static_data(
                                eid BIGINT NOT NULL REFERENCES static_events(eid),
                                tid BIGINT NOT NULL REFERENCES geolondon(tid)
                                )""")
                print "> Table cluster_static_data created"
            elif args[i]=="tweets":
                cursor.execute("""CREATE TABLE tweets(
                                tid BIGINT NOT NULL,
                                uname VARCHAR(40) NOT NULL,
                                rname VARCHAR(40),
                                created_at TIMESTAMP,
                                location VARCHAR(128),
                                text VARCHAR(200),
                                geolocation GEOGRAPHY(POINT, 4326),
                                probability DECIMAL,
                                profanity VARCHAR(1),
                                PRIMARY KEY (tid)
                                )""")
                cursor.execute("CREATE INDEX tweets_index ON tweets(tid)")
                cursor.execute("CREATE INDEX tweets_geo_index ON tweets USING GIST (geolocation)")
                print "> Table tweets created"
            elif args[i]=="cameras":
                cursor.execute("""CREATE TABLE cameras(
                                title TEXT,
                                link TEXT,
                                description TEXT,
                                geolocation GEOGRAPHY(POINT, 4326)
                                )""")
                cursor.execute("CREATE INDEX cameras_index ON cameras USING GIST (geolocation)")
                print "> Table tweets created"
            elif args[i]=="tweets_metrics":
                cursor.execute("""CREATE TABLE tweets_metrics(
                                total_tweets BIGINT,
                                traffic_tweets BIGINT,
                                rightturn_tweets BIGINT,
                                retweets BIGINT,
                                geotweets BIGINT,
                                foundgeotweets BIGINT
                                )""")
                cursor.execute("""INSERT INTO tweets_metrics VALUES(0,0,0,0,0,0)""")
                print "> Table tweets_metrics created"
            elif args[i]=="geolookup":
                cursor.execute("""CREATE TABLE geolookup(
                                screetaddress TEXT NOT NULL,
                                soundex TEXT,
                                latlon GEOGRAPHY(POINT, 4326),
                                PRIMARY KEY (streetaddress)
                                )"""
                print "> Table geolookup created"

        print "> Giving privileges"
        configSection = "Users"
        Config = ConfigParser.ConfigParser()
        Config.read("t4t_credentials.txt")
        users = {}
        users[0] = Config.get(configSection, "user1")
        users[1] = Config.get(configSection, "user2")
        users[2] = Config.get(configSection, "user3")
        users[3] = Config.get(configSection, "user4")
        users[4] = Config.get(configSection, "user5")
        users[5] = Config.get(configSection, "user6")

        for i in range(1,len(args)):
            for j in users:
                query = "GRANT ALL PRIVILEGES ON " + args[i] + " TO " + users[j]
                cursor.execute(query)
                
        
        conn.commit()
        print "> T4T DB setup completed"

    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Table create failed! -> %s" % (exceptionType))

###############################################################################################
################### Removes all values from the tables of the database ########################
###############################################################################################

def rmv(cursor, conn, *args):
    try:
        print "> Removing values..."
        for i in range(1,len(args)):
            query = "DELETE FROM %s" % args[i]
            cursor.execute(query)
            print "> Removed values from %s" % args[i]

        conn.commit()
        print "> T4T DB tables cleared"
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Remove values failed! -> %s" % (exceptionValue))

###############################################################################################
########################## Drops all the tables of the database ###############################
###############################################################################################

def drop(cursor, conn, *args):
    try:
        print "> Dropping tables..."

        for i in range(1,len(args)):
            query = "DROP TABLE %s" % args[i]
            cursor.execute(query)
            print "> Dropping table %s" % args[i]

        conn.commit()
        print "> T4T DB tables dropped"
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Table drop failed! -> %s" % (exceptionValue))


if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")

    # Parse options from the command line
    parser = optparse.OptionParser("usage: %prog [options] [action] [tables]")
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
    parser.add_option('-p','--password',
                    dest='password',
                    default=password,
                    help='The password for the DB')

    (options, args) = parser.parse_args()

    db = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    # Needs an argument (setup, remove or drop)
    if len(args)==0:
        sys.exit("Wrong number of arguments")

    sys.exit(main(args[0], *args, **db))
