from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import time
from datetime import datetime, timedelta

def main(maxDistance,minPoints,maxTime):
    date = datetime.now()
    updated_at = date.strftime("%d/%m/%y %H:%M:%S")
        
    timeToSearch = date-timedelta(minutes=maxTime)
    timeToSearch = timeToSearch.strftime("%d/%m/%y %H:%M:%S")
    deleteClusters()
    createClusters(maxDistance,minPoints,timeToSearch);

    print "Calculate mean and variance"
    calculateMeanAndVariance()
    try:
        conn.commit()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Commit error! ->%s" % (exceptionValue))

    print "Event Clusters Updated @%s" % updated_at
    
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

def deleteClusters():
    try:
        query = """DELETE FROM cluster_static_data"""
        cursor.execute(query)
        query = """DELETE FROM static_events WHERE eid!='0'"""
        cursor.execute(query)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Error in deleteClusters! -> %s" % (exceptionValue))


def createClusters(maxDistance,minPoints,timeToSearch):
    try:
        query = """SELECT tid, ST_AsText(geolocation) FROM geolondon WHERE
        geolocation IS NOT NULL AND created_at >= '%s'""" % timeToSearch

        cursor.execute(query)
        pointRows = cursor.fetchall()
        
            
        clustered = []
        for point in pointRows:
            tid, longitude, latitude = pointRow2vars(point)
            
            #look if tid is already clustered
            if tid not in clustered:
                neighbourPointRows = findNeighbourPoints(longitude,latitude,maxDistance,timeToSearch)
            
                if len(neighbourPointRows)>=minPoints:
                    print len(neighbourPointRows)
                    clustered.append(tid) # add the first point of the cluster in the list
                    createNewCluster(maxDistance,minPoints,timeToSearch,tid,neighbourPointRows,clustered)
                else:
                    addInCluster(0,tid) # eid 0 for no cluster
                    clustered.append(tid) # add in the clustered points list
            
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Error in createClusters! -> %s" % (exceptionValue))
        
def createNewCluster(maxDistance,minPoints,timeToSearch,tid,neighbourPointRows,clustered):
    try:
        # create new cluster
        query = """INSERT INTO static_events(meanX,varianceX,meanY,varianceY)
        VALUES(NULL,NULL,NULL,NULL)"""
        cursor.execute(query)
        
        # find the new cluster's id
        query = """SELECT last_value FROM static_events_eid_seq"""
        cursor.execute(query)
        answer = cursor.fetchall()
        eid = answer[0][0]
        
        # add tid in cluster
        addInCluster(eid,tid)
        
        neighbourPointList = []
        neighbourPointList.extend(neighbourPointRows)
        
        for point in neighbourPointList:
            tid, longitude, latitude = pointRow2vars(point)
            
            if tid not in clustered:
                newNeighbourPointRows = findNeighbourPoints(longitude,latitude,maxDistance,timeToSearch)
                
                if len(newNeighbourPointRows)>=minPoints:
                    addInCluster(eid,tid)
                    appendDistinct(neighbourPointList,newNeighbourPointRows)
                    clustered.append(tid)
                else:
                    addInCluster(0,tid) # eid 0 for no cluster
                    clustered.append(tid)
        
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Error in createNewCluster! -> %s" % (exceptionValue))

def appendDistinct(list, rows):
    for object in rows:
        if object not in list:
            list.append(object)
        
def pointRow2vars(point):
    tid = point[0]
    coordinates = point[-1][6:-1]
    lonlatArray = coordinates.split(" ")
    longitude = lonlatArray[0]
    latitude = lonlatArray[1]
    
    return tid, longitude, latitude
    
def findNeighbourPoints(longitute,latitude,maxDistance,timeToSearch):
    try:
        query = """SELECT tid, ST_AsText(geolocation)
                    FROM geolondon
                    WHERE ST_DWithin(geolocation,'POINT(%s %s)', %s)
                    AND created_at >= '%s'""" % (longitute,latitude,maxDistance,timeToSearch)
        cursor.execute(query)
        neighbourPointRows = cursor.fetchall()
        return neighbourPointRows
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Error in findNeighbourPoints! -> %s" % (exceptionValue))
    
def addInCluster(eid, tid):
    try:
        query = """INSERT INTO cluster_static_data VALUES(%s,%s)""" % (eid, tid)
        cursor.execute(query)
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Error in addInCluster! -> %s" % (exceptionValue))
        

def calculateMeanAndVariance():
    try:
        query = """SELECT eid, AVG(X(ST_AsText(geolocation))),
                    VARIANCE(X(ST_AsText(geolocation))), AVG(Y(ST_AsText(geolocation))),
                    VARIANCE(Y(ST_AsText(geolocation))) FROM geolondon,cluster_static_data
                    WHERE geolocation IS NOT NULL AND geolondon.tid=cluster_static_data.tid
                    AND eid<>0 GROUP BY eid"""

        cursor.execute(query)
        clusterRows = cursor.fetchall()

        for row in clusterRows:
            query = """UPDATE static_events SET variancex=%s, meanx=%s,
            variancey=%s, meany=%s WHERE eid=%s""" % (row[1],row[2],row[3],row[4],row[0])
            print query

            cursor.execute(query)

    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

        sys.exit("Error in calculateMeanAndVariance! -> %s" % (exceptionValue))



if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")

    # Parse options from the command line
    parser = optparse.OptionParser("usage: %prog [options] arg1")
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
    parser.add_option('-D','--distance',
                    dest='distance',
                    default='50',
                    help='Maximum event distance')
    parser.add_option('-T','--time',
                    dest='time',
                    default='10000000',
                    help='Minutes to search for tweets')
    parser.add_option('-N','--ntweets',
                    dest='ntweets',
                    default='50',
                    help='Number of tweets for cluster')

    (options, args) = parser.parse_args()

    db = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('distance','time','ntweets'))
    kwds = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('host','database','user','password'))
    
    cursor, conn = connect(**db)
    
    sys.exit(main(int(kwds['distance']),int(kwds['ntweets']),int(kwds['time'])))
