"""
Module for harvesting tweets from twitter search api.
Typical calling command:
$ python uktwaffic -t 'traffic OR accident OR tailback OR gridlock OR m25 OR standstill OR road OR street OR stuck OR car OR bus OR train' database_file.sqlite 
## if you only want tweets with an id higher than MINID then use this (better search terms too)
$ python uktwaffic -i ${MINID} -t 'traffic OR accident OR tailback OR gridlock OR m25 OR standstill OR road OR street OR stuck OR car OR bus OR train OR signals OR incident -web -google -marketing' database_file.sqlite 
"""
import os
import sys
import sqlite3
from sqlite3 import OperationalError
import twitter
from twitter import TwitterError
from urllib2 import URLError
import time
from datetime import datetime
DATETIME_STRING_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
DATETIME_STAMP_STRING_FORMAT = '%Y%m%d%H%M%S'
from logging import FATAL, ERROR, WARNING, INFO, DEBUG

if __name__ == '__main__':
    import sys
    sys.path.append('..')

from crawler import GetRateLimiter, SuppressedCallException

def robust_execute(conn,cursor,query,values=None, maxtries=5):
    success = False
    tries = 0
    while True:
        try:
            if values is None:
                cursor.execute(query)
            else:
                cursor.execute(query,values)
            conn.commit()
            success = True
        except OperationalError, oe:
            print "Query Failed: ", query, values
            print "Error: ", oe
            if tries < maxtries:
                tries += 1
                print "Retrying..."
            else:
                raise
        if success == True:
            break


def geolondon(  conn,
                rl,
                georadius="19.622mi",
                term='traffic',
                start_id=0,
                **kwargs):
    cursor = conn.cursor()
    most_recent_id = start_id
    geocount = 0
    while True:
        since_id = most_recent_id
        results = None
        page = 0
        print "Getting results since ", since_id
        while results != [] and page <= 15:
            page += 1
            try:
                print "Getting results page:", page
                print "georadius", georadius
                searchargs = dict(geocode=(51.5,-0.15,georadius),per_page=100,page=page,since_id=since_id,term=term)
                print "[twitter] rl.FreqLimitGetSearch - %r" % searchargs
                results = rl.FreqLimitGetSearch(**searchargs)
                for r in results:
                    most_recent_id = max(r.id,most_recent_id)
                    (tid,uname,created_at_str,location,text,geo) = r.id,r.user.screen_name,r.created_at,r.location,r.text,r.GetGeo()
                    created_at = datetime.strptime(created_at_str, DATETIME_STRING_FORMAT)
                    text = text.encode('ascii','ignore')
                    now = datetime.now()
                    nowstr = datetime.strftime(now, DATETIME_STRING_FORMAT)
                    print "a result at: ",nowstr
                    print (tid,uname,created_at,location,text,geo)
                    # geo part
                    if not geo is None and geo.get('type') == 'Point':
                        geolat,geolong, = geo['coordinates']
                        geocount += 1
                        print "\t### got one at: ", geo['coordinates'], "that makes %d" % geocount
                        # and the call
                        query = "INSERT OR IGNORE INTO geolondon(tid,uname,created_at,location,text,geolat,geolong)"\
                              + " VALUES(?,?,?,?,?,?,?)"
                        params = (tid,uname,created_at,location,text,geolat,geolong)
                        print "[sql] cursor.execute( %s , %r) " % ( query , params )
                        cursor.execute( query, params)
                    else:
                        print "Not geo tagged"
                        cursor.execute("INSERT OR IGNORE INTO geolondon(tid,uname,created_at,location,text)"\
                        +" VALUES(?,?,?,?,?)" , (tid,uname,created_at,location,text))
                    conn.commit()
            except TwitterError, e:
                print
                print "[ERROR] TwitterError: ", e, "page:",page, "since_id",since_id
                results = []
                print
            except URLError, e:
                print "[ERROR] URLError: ", e, "page:",page, "since_id",since_id
                results = []
 #           except Exception, e:
 #               print
 #               print "[ERROR] ", e
 #               results = []
 #               print


#def sqlexecute(conn, cursor, query, params, verbosity)
#    print "[sql] cursor.execute( %s , %r) " % ( query , params )
#    cursor.execute( query, params)

def main(*args,**kwargs):
    if kwargs['verbosity'] <= DEBUG:
        print "[debug] main args", args
        print "[debug] main kwargs", kwargs
    if len(args) >= 1:
        sqlfile = args[0]
        kwargs['sqlfile'] = sqlfile
    else:
        sqlfile = kwargs['sqlfile']
    if kwargs['verbosity'] <= INFO:
        print "sql file", sqlfile
    conn = sqlite3.connect(sqlfile)
    cursor = conn.cursor()

    if kwargs['query_max_id']:
        print get_max_id(conn,cursor)
        return

    # else run full program
    fileparts = sqlfile.rpartition(os.sep)
    datadir = fileparts[0]
    fileid = fileparts[-1].rpartition('.')[0]
    epsofname =  datadir + os.sep + fileid + '.eps'
    print "epsofname = ", epsofname

    query = 'CREATE TABLE IF NOT EXISTS geolondon(tid INTEGER PRIMARY KEY,uname VARCHAR(40), created_at DATETIME,location VARCHAR(128), text VARCHAR(150), geolat FLOAT, geolong FLOAT )'
    params = None
    print "[sql] cursor.execute( %s , %r) " % ( query , params )
    cursor.execute(query)
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS geolon_tid_idx ON geolondon(tid)')
    conn.commit()



    query = 'CREATE TABLE IF NOT EXISTS options (timestamp DATETIME, key TEXT, value TEXT, UNIQUE(timestamp, key))'
    params = None
    print "[sql] cursor.execute( %s , %r) " % ( query , params )
    cursor.execute(query)
    timestamp = datetime.now()
    for key,value in kwargs.iteritems():
        query = 'INSERT OR IGNORE INTO options VALUES(?,?,?)'
        params = (timestamp, key, value)
        print "[sql] cursor.execute( %s , %r) " % ( query , params )
        cursor.execute( query, params)
    conn.commit()

    start_id = get_max_id(conn,cursor)
    print start_id
    if start_id is not None:
        kwargs['start_id'] = int(start_id)

    rl = GetRateLimiter()
    rl.api._cache_timeout = 30
    geolondon(conn,rl,**kwargs)


def get_max_id(conn,cursor):
    query = 'SELECT MAX(tid) FROM geolondon'
    cursor.execute(query)
    ((start_id,),) = cursor.fetchall()
    return start_id

if __name__ == '__main__':
    import StringIO
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--sqlfile',
                        dest='sqlfile',
                        default=None,
                        help='The input sql file name')
    parser.add_option('-i',
                        dest='start_id',
                        type=int,
                        default=0,
                        help='Start id to scan from')
    parser.add_option('-r',
                        dest='georadius', 
                        default='20.0mi', 
                        help='The radius of the geocode entry')
    parser.add_option('-t',
                        dest='term', 
                        default='traffic OR accident OR tailback OR gridlock OR m25 OR standstill', 
                        help='The search term for the search api')
    parser.add_option('-v', '--verbosity',
                        dest='verbosity', 
                        default=WARNING, 
                        type=int,
                        help='Set the verbosity')
    parser.add_option('-x', '--query-max-id',
                        dest='query_max_id', 
                        default=False, 
                        action ='store_true',
                        help='Simply return the maximum id currently in the table')

    (options, args) = parser.parse_args()
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
#    print "args",args
#    print "kwargs",kwargs
    main(*args,**kwargs)


