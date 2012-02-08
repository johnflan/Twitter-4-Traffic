from pg8000 import DBAPI
import sys
import optparse
import ConfigParser

def main(**db):
    # Connect to the db
    cursor, conn = connect(**db)
    
    label_tweets(cursor, conn)
    
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
############################  ###################################
###############################################################################################

def label_tweets(cursor, conn):
    i=0
    lastid="0"
    while True:
        try:
            query = "SELECT tid, text FROM geolondon WHERE tid NOT IN (SELECT tid FROM labelled_tweets) ORDER BY RANDOM() LIMIT 1"
            cursor.execute(query)
            data = cursor.fetchone()
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Select Error -> %s" % exceptionValue
            lastid="0"
            continue

        try:
            print ">>> Tweet %s: %s <<<" % (data[0], data[1])
            print "> \'1\' Traffic - \'2\' Not Traffic - \'3\' Unclear - \'4\' Bot / \'r\' Remove previous row \'q\' Quit"
            ch = raw_input("> Enter a choice: ")

            choice = {}
            if ch=="1":
                choice[0]='y'
                choice[1],choice[2],choice[3]='n','n','n'
            elif ch=="2":
                choice[1]='y'
                choice[0],choice[2],choice[3]='n','n','n'
            elif ch=="3":
                choice[2]='y'
                choice[0],choice[1],choice[3]='n','n','n'
            elif ch=="4":
                choice[3]='y'
                choice[0],choice[1],choice[2]='n','n','n'
            elif ch=="q":
                print "%s tweets labelled" % i
		return
            elif ch=="r":
		if lastid!="0":
                    query = "DELETE FROM labelled_tweets WHERE tid='%s'" % lastid
                    cursor.execute(query)
                    conn.commit()
                    print "> Tweet %s removed" % lastid
                    lastid="0"
                    i-=1
                    continue
                else:
                    continue
            else:
                print "> Wrong key"
                continue

            cursor.execute("INSERT INTO labelled_tweets VALUES(%s,%s,%s,%s,%s,%s)", (data[0],data[1],choice[0],choice[1],choice[2],choice[3]))
            conn.commit()
            lastid=data[0]
            i+=1
            print "Saved Tweet: %s" % data[0]
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Insert Error -> %s" % exceptionValue
            lastid="0"
        
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

    sys.exit(main(**db))
