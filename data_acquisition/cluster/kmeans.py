from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import math
from datetime import datetime

def main(clusters, from_hour, to_hour):
    date = datetime.now()
    updated_at = date.strftime("%d/%m/%y %H:%M:%S")

    deleteClusters()
    print "Old clusters deleted"
    createClusters(clusters, from_hour, to_hour);

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
        query = """DELETE FROM static_events"""
        cursor.execute(query)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Error in deleteClusters! -> %s" % (exceptionValue))


def distance(loc1, loc2):
    # Euclidean distance sqrt(sum((a[i]-b[i])^2)
    ret = 0.0
    for i in range(0,len(loc1)):
        ret += (loc1[i]-loc2[i])**2
    return math.sqrt(ret) 


def addInCluster(cid, tid, longt, lat, clist):
    loc = {tid: [float(longt), float(lat)]}
    if cid in clist.keys():
        clist[cid].append(loc)
    else:
        clist[cid] = [loc]
    return clist


def avg2D(a):
    temp = [0,0]
    for b in a:
        temp[0] += b.values()[0][0]
        temp[1] += b.values()[0][1]
    temp[0] /= len(a)
    temp[1] /= len(a)
    return temp


def findNewCenters(centers, points):
    data = {}
    clusters = len(centers)
    for point in points:
        tid, longitude, latitude = pointRow2vars(point)
        min_dist = distance([longitude, latitude], centers[0])
        cluster = 1
        for i in range(1,clusters):
            dist = distance([longitude, latitude], centers[i])
            if min_dist > dist:
                min_dist = dist
                cluster = i+1
        addInCluster(cluster, tid, longitude, latitude, data)
    new_centers = []
    for i in range(1,clusters+1):
        temp = avg2D(data[i])
        new_centers.append(temp)
    return new_centers, data


def notEquals(centers, new_centers):
    for i in range(0,len(centers)):
        if centers[i][0] != new_centers[i][0] or centers[i][1] != new_centers[i][1]:
            return True
    return False


def pointRow2vars(point):
    tid = point[0]
    coordinates = point[-1][6:-1]
    lonlatArray = coordinates.split(" ")
    longitude = lonlatArray[0]
    latitude = lonlatArray[1]
    return tid, float(longitude), float(latitude)


def createClusters(clusters, from_hour, to_hour):
    try:
        query = """SELECT DISTINCT tid, ST_AsText(geolocation) FROM geolondon WHERE
        geolocation IS NOT NULL AND extract(hour from created_at) >= '%s' and
        extract(hour from created_at) <= '%s'""" % (from_hour, to_hour)

        cursor.execute(query)
        pointRows = cursor.fetchall()

        if pointRows < clusters:
            sys.exit("Less points given than the clusters you want");

        centers = []
        for i in range(0,clusters): #select first n elements as initial means
            tid, longitude, latitude = pointRow2vars(pointRows[i])
            centers.append([longitude, latitude])        

        new_centers, data = findNewCenters(centers, pointRows)

        while notEquals(centers, new_centers):
            centers = new_centers
            new_centers, data = findNewCenters(centers, pointRows)
        print "New centers:"
        print new_centers
        print

        writeInDB(data)
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        sys.exit("Error in createClusters! -> %s" % (exceptionValue))

def writeInDB(data):
    for cluster in data.values():
        # create new cluster
        query = """INSERT INTO static_events(meanX,varianceX,meanY,varianceY)
                VALUES(NULL,NULL,NULL,NULL)"""
        cursor.execute(query)

        # find the new cluster's id
        query = """SELECT last_value FROM static_events_eid_seq"""
        cursor.execute(query)
        answer = cursor.fetchall()
        eid = answer[0][0]

        for tweet in cluster:
            # add tid in cluster
            try:
                query = """INSERT INTO cluster_static_data VALUES(%s,%s)""" % (eid,
                        int(tweet.keys()[0]))
                cursor.execute(query)
            except:
                # Get the most recent exception
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                # Exit the script and print an error telling what happened.
                print "For values "+str(eid)+", "+str(tweet.keys()[0])
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
            query = """UPDATE static_events SET variancex=%s, meanx=%s, variancey=%s, meany=%s WHERE eid=%s""" % (row[2],row[1],row[4],row[3],row[0])
            print query

            cursor.execute(query)

    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

        sys.exit("Error in calculateMeanAndVariance! -> %s" % (exceptionValue))



if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("../t4t_credentials.txt")
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
    parser.add_option('-n','--clusters',
                    dest='clusters',
                    default='3',
                    help='Number of clusters')
    parser.add_option('-f','--from_hour',
                    dest='from_hour',
                    default='9',
                    help='From hour to search the tweets')
    parser.add_option('-t','--to_hour',
                    dest='to_hour',
                    default='10',
                    help='To hour to search the tweets')

    (options, args) = parser.parse_args()

    db = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('clusters','from_hour','to_hour'))
    kwds = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('host','database','user','password'))
    
    cursor, conn = connect(**db)
    
    sys.exit(main(int(kwds['clusters']),kwds['from_hour'],kwds['to_hour']))
