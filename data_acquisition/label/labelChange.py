from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import os
import termios
import fcntl



def getch():
  fd = sys.stdin.fileno()

  oldterm = termios.tcgetattr(fd)
  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)

  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

  try:        
    while 1:            
      try:
        c = sys.stdin.read(1)
        break
      except IOError: pass
  finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  return c
  
  
def main(**db):
    # Connect to the db
    cursor, conn = connect(**db)

    label_tweets(cursor, conn, db['user'])
    
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
####################### Change The Classification Of Traffic Tweets ###########################
###############################################################################################

def label_tweets(cursor, conn, username):
    lastid="0"
    row=1
    numRows=0
    selectedRow=0
    
    try:
        query = """SELECT labelled_tweets.tid, uname, tweet FROM
        labelled_tweets, geolondon WHERE labelled_tweets.tid=geolondon.tid AND ptraffic='y'"""
        cursor.execute(query)
        allRows = cursor.fetchall()
        numRows = len(allRows)
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Select Error -> %s" % exceptionValue)
        
    try:
        print "> There are %s rows" % len(allRows)
        ch = raw_input("> Select a row (1 for the first): ")
        selectedRow = int(ch)
        if selectedRow<=0 or selectedRow>len(allRows):
            sys.exit(" Selected Row Out Of Bounds")
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Error -> %s" % exceptionValue)
    
    row = selectedRow
    for i in range(selectedRow-1,len(allRows)):
        data=allRows[i]
        try:
            print "\n\n\n\nRow:  #%s of %s\nUser:  @%s" % (row,numRows,data[1])
            print "\n%s\n" % data[2]
            print "\'2\' Move To Not Traffic \'3\' Move To Unclear \'4\' Move To Bot \'Enter\' To Continue \'r\' Move previous row to traffic \'q\' Quit"

            ch = getch()
                
            choice = {}
            if ch=='2':
                choice[1]='y'
                choice[0],choice[2],choice[3]='n','n','n'
            elif ch=='3':
                choice[2]='y'
                choice[0],choice[1],choice[3]='n','n','n'
            elif ch=='4':
                choice[3]='y'
                choice[0],choice[1],choice[2]='n','n','n'
            elif ch=='q':
                showUserStats(cursor)
                return
            elif ch=='r':
                if lastid!="0":
                    choice[0]='y'
                    choice[1],choice[2],choice[3]='n','n','n'
                    cursor.execute("UPDATE labelled_tweets SET ptraffic=%s, ntraffic=%s, unclear=%s, robot=%s WHERE tid=%s", 
                    (choice[0],choice[1],choice[2],choice[3],data[0]))
                    conn.commit()
                    print "> Tweet %s moved to traffic" % lastid
                    lastid="0"
                    row+=1
                    numRows+=1
                    continue
                else:
                    continue
            else:
                row+=1
                continue

            cursor.execute("UPDATE labelled_tweets SET ptraffic=%s, ntraffic=%s, unclear=%s, robot=%s WHERE tid=%s", 
                    (choice[0],choice[1],choice[2],choice[3],data[0]))
            conn.commit()
            lastid=data[0]
            row-=1
            numRows-=1
            print "Changed Tweet: %s" % data[0]
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Insert Error -> %s" % exceptionValue
            lastid="0"

    print "\n\n\n\nEND OF ROWS"
            
def showUserStats(cursor):
    try:
        query = "SELECT username, count(*) as labels FROM labelled_tweets GROUP BY username ORDER BY labels DESC"

        cursor.execute(query)

        users = cursor.fetchall()

        print ">>>>>>  Statistics  <<<<<<"
        total=0

        for user in users:
            print "User: %s Labelled: %s" % (user[0],user[1])
            total+=int(user[1])

        print "Total %s Tweets Labelled" % total

    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Error -> %s" % exceptionValue)

if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("../t4t_credentials.txt")
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
