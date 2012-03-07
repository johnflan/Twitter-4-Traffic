from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import time
from datetime import datetime, timedelta
import math

def main(maxDistance,minPoints,maxTime):
    date = datetime.now()
    updated_at = date.strftime("%d/%m/%y %H:%M:%S")

    timeToSearch = date-timedelta(minutes=maxTime)
    timeToSearch = timeToSearch.strftime("%d/%m/%y %H:%M:%S")
    print "\nSearching from time: "+timeToSearch
    clusters = createClusters(maxDistance,minPoints,timeToSearch)
    print clusters
    print "\n"

    try:
        query = """SELECT variancex, meanx,variancey, meany, eid FROM static_events"""
        cursor.execute(query)
        static_clusters = cursor.fetchall()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Select error! ->%s" % (exceptionValue))

    for key in clusters.keys():
        if key == 0:
            continue
        s2x = 0
        sx = 0
        s2y = 0
        sy = 0
        for value in clusters[key]:
            sx += value[0]
            sy += value[1]
        mx = sx/len(clusters[key])
        my = sy/len(clusters[key])
        for value in clusters[key]:
            s2x += (value[0] - mx)**2
            s2y += (value[1] - my)**2
        vx = s2x/len(clusters[key])
        vy = s2y/len(clusters[key])

        for static_cluster in static_clusters:
            prob = pdfGaussian2D(mx, my, static_cluster[1], static_cluster[3],
                    static_cluster[0], static_cluster[2])
            print prob
            if prob > 0.5:
                print "Cluster with center ("+mx+","+my+") belongs to cluster with id "+static_cluster[4]+" with probability "+prob

    #try:
        #conn.commit()
    #except:
    #    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    #    sys.exit("Commit error! ->%s" % (exceptionValue))

    #print "Event Slice Clusters Updated @%s" % updated_at


def pdfGaussian2D(x, y, mx, my, vx, vy):
    print x
    print y
    print mx
    print my
    print vx
    print vy
    return (1.0/
            (2*math.pi*math.sqrt(vx)*math.sqrt(vy))*
                math.exp(-0.5*((x-mx)*(x-mx)/vx + (y-my)*(y-my)/vy -
                2*r*(x-mx)*(y-my)/(math.sqrt(vx)*math.sqrt(vy)))))

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


def createClusters(maxDistance,minPoints,timeToSearch):
   # try:
        query = """SELECT tid, ST_AsText(geolocation) FROM tweets WHERE
            geolocation IS NOT NULL AND created_at >= '%s'""" % timeToSearch

        cursor.execute(query)
        pointRows = cursor.fetchall()


        clustered = []
        counter = 1
        clusters = {}
        for point in pointRows:
            tid, longitude, latitude = pointRow2vars(point)

            #look if tid is already clustered
            if tid not in clustered:
                neighbourPointRows = findNeighbourPoints(longitude,latitude,maxDistance,timeToSearch)

                if len(neighbourPointRows) >= minPoints:
                    clustered.append(tid) # add the first point of the cluster in the list
                    cluster_temp = createNewCluster(maxDistance,minPoints,timeToSearch,tid,neighbourPointRows,clustered,counter,
                            float(longitude), float(latitude))
                    for key in cluster_temp.keys():
                        clusters[key] = cluster_temp[key]
                    counter = counter + 1
                else:
                    clusters = addInCluster(0,[float(longitude),
                        float(latitude)],clusters) # eid 0 for no cluster
                    clustered.append(tid) # add in the clustered points list
        return clusters
    #except:
        # Get the most recent exception
     #   exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
      #  sys.exit("Error in createClusters! -> %s" % (exceptionValue))

def createNewCluster(maxDistance,minPoints,timeToSearch,tid,neighbourPointRows,clustered,eid, init_long, init_lat):
    try:
        cluster_list = {}
        # add tid in cluster
        cluster_list = addInCluster(eid,[init_long, init_lat],cluster_list)

        neighbourPointList = []
        neighbourPointList.extend(neighbourPointRows)

        for point in neighbourPointList:
            tid, longitude, latitude = pointRow2vars(point)

            if tid not in clustered:
                newNeighbourPointRows = findNeighbourPoints(longitude,latitude,maxDistance,timeToSearch)

                if len(newNeighbourPointRows)>=minPoints:
                    cluster_list = addInCluster(eid, [float(longitude), float(latitude)], cluster_list)
                    appendDistinct(neighbourPointList,newNeighbourPointRows)
                    clustered.append(tid)
                else:
                    cluster_list = addInCluster(0, [float(longitude), float(latitude)], cluster_list) # eid 0 for no cluster
                    clustered.append(tid)
        return cluster_list
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
                    FROM tweets
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

def addInCluster(eid, loc, clist):
    if eid in clist.keys():
        clist[eid].append(loc)
    else:
        clist[eid] = [loc]
    return clist


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
    parser.add_option('-D','--distance',
                    dest='distance',
                    default='5000',
                    help='Maximum event distance')
    parser.add_option('-T','--time',
                    dest='time',
                    default='1440',
                    help='Minutes to search for tweets')
    parser.add_option('-N','--ntweets',
                    dest='ntweets',
                    default='3',
                    help='Number of tweets for cluster')

    (options, args) = parser.parse_args()

    db = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('distance','time','ntweets'))
    kwds = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('host','database','user','password'))
    
    cursor, conn = connect(**db)
    
    sys.exit(main(int(kwds['distance']),int(kwds['ntweets']),int(kwds['time'])))
