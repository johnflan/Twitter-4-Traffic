#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import nltk
import re


features = []

def main(*args,**opts):
    db = dict([ ['host',opts['host']], ['database',opts['database']],
        ['user',opts['user']], ['password',opts['password']]])

    cursor,conn = connectDB(**db)
    
    #check if to_table exists otherwise create
    cursor.execute("SELECT relname FROM pg_class WHERE relname='"
            +opts['to_table']+"'")
    if len(cursor.fetchall()) < 1:
        try:
            cursor.execute("CREATE TABLE "+opts['to_table']+
                    " (word TEXT PRIMARY KEY, freq numeric)")

        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            sys.exit("Creating stop words table failed! ->%s" % (exceptionValue))

    cursor.execute("SELECT "+opts['column']+" FROM "+opts['from_table'])

    rows = cursor.fetchall()
    all_words = []
    for row in rows:
        row = row[0].replace("'","").replace("%","")
        row = re.sub("\W"," ",row)


        words = [word.lower() for word in row.split()]
        all_words.extend(words)

    wordlist = nltk.FreqDist(all_words)

    for i in range(min(len(wordlist),int(opts['limit']))):
        print wordlist.keys()[i]
        #if already in database update frequency
        try:
            cursor.execute("SELECT * FROM %s  WHERE word= '%s'" % (opts['to_table'], wordlist.keys()[i]))
            if len(cursor.fetchall()) > 0:
                cursor.execute("UPDATE %s SET freq=%s WHERE word='%s'" % (opts['to_table'],wordlist.values()[i],wordlist.keys()[i]))
            else:
                cursor.execute("INSERT INTO %s (word,freq) VALUES('%s',%s)" %
                        (opts['to_table'],wordlist.keys()[i],wordlist.values()[i]))
		conn.commit()
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            sys.exit("Could not write/update values in database! ->%s" % (exceptionValue))
    #todo: keep only so many data..



def connectDB(**db):
    try:
        conn = DBAPI.connect(**db)
        cursor = conn.cursor()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Database connection failed! ->%s" % (exceptionValue))
    return cursor, conn


if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")
    to_table = 'stop_words'
    from_table = 'geolondon'
    column = 'text'
    limit = 500

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

    parser.add_option('-f','--from_table',
                    dest='from_table',
                    default=from_table,
                    help='The table the tweets are stored in')
    parser.add_option('-c','--column',
                    dest='column',
                    default=column,
                    help='The column the text is stored in')
    parser.add_option('-t','--to_table',
                    dest='to_table',
                    default=to_table,
                    help='The table for the stop words')
    parser.add_option('-l','--limit',
                    dest='limit',
                    default=limit,
                    help='How many stop words will be stored')

    (options, args) = parser.parse_args()

    opts = dict([ [k,v] for k,v in options.__dict__.iteritems() if not v is
        None ])
    sys.exit(main(*args,**opts))
