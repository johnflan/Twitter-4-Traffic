from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import datetime
import math

def main(clusters,maxTime):
    #last entry in geolondon is 2012-03-03 02:17:18
    d = datetime.date(2012,3,3)
    t = datetime.time(2,17,18)
    last_date = datetime.datetime.combine(d,t)

    timeToSearch = last_date - datetime.timedelta(minutes=maxTime)
    timeToSearch = timeToSearch.strftime("%d/%m/%y %H:%M:%S")
    print "\nSearching from time: " + timeToSearch
    centers, clusters = createClusters(clusters,timeToSearch)

    try:
        query = """SELECT variancex, meanx,variancey, meany, eid FROM static_events"""
        cursor.execute(query)
        static_clusters = cursor.fetchall()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Select error! ->%s" % (exceptionValue))

    i = 0
    for key in clusters.keys():
        s2x = 0
        sx = 0
        s2y = 0
        sy = 0
        for point in clusters[key]:
            s2x += (point.values()[0][0] - centers[i][0])**2
            s2y += (point.values()[0][1] - centers[i][1])**2
        vx = s2x/len(clusters[key])
        vy = s2y/len(clusters[key])

        print "New cluster "+str(centers[i][0])+" "+str(centers[i][1])
        for static_cluster in static_clusters:
            dif = kl(centers[i], [vx, vy], [static_cluster[1], static_cluster[3]],
                    [static_cluster[0], static_cluster[2]])
            print str(static_cluster[1])+" "+str(static_cluster[3])+": "+str(dif)
        print
        i += 1


def kl(m1, v1, m0, v0):
    m0 = [float(m0[0]), float(m0[1])]
    v0 = [float(v0[0]), float(v0[1])]
    mx = (m1[0] - m0[0])**2
    my = (m1[1] - m0[1])**2
    return 0.5*(v0[0]*v1[1] + v1[0]*v0[1] + mx*v1[1] + my*v1[0] -
            math.log(v0[0]*v0[1]/(v1[0]*v1[1])))


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


def createClusters(clusters,timeToSearch):
    #try:
        query = """SELECT DISTINCT tid, ST_AsText(geolocation) FROM geolondon WHERE
        geolocation IS NOT NULL AND created_at >= '%s'""" % timeToSearch

        cursor.execute(query)
        pointRows = cursor.fetchall()

        numOfCl = math.floor(math.sqrt(len(pointRows)/2.0))
        if clusters > numOfCl:
            clusters = numOfCl

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

        return new_centers, data
    #except:
        # Get the most recent exception
     #   exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
     #   sys.exit("Error in createClusters! -> %s" % (exceptionValue))


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
                    default='6',
                    help='Number of clusters')
    parser.add_option('-T','--time',
                    dest='time',
                    default='5760',
                    help='Minutes to search for tweets')

    (options, args) = parser.parse_args()

    db = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('clusters','time'))
    kwds = dict([k,v] for k,v in options.__dict__.iteritems() if not v is None
            and k not in ('host','database','user','password'))
    
    cursor, conn = connect(**db)
    
    sys.exit(main(int(kwds['clusters']),int(kwds['time'])))
