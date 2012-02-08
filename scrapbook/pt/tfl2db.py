from pg8000 import DBAPI
from xml.dom.minidom import parseString
from math import *
import sys
import optparse
import ConfigParser
import time
from time import strftime
import urllib2

def main(**kw):
    # Connect to the db
    db = dict([[k,v] for k,v in kw.iteritems() if k!='email' and k!='feedid'])
    cursor, conn = connect(**db)

    t1 = time.time()
    periodically_sample_feed(cursor, conn, **kw)
    t2 = time.time()
    print "%0.3f" % (t2-t1)

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
############################# Loads an xml feed from tfl ######################################
###############################################################################################

def periodically_sample_feed(cursor, conn, **kw):
    url = 'http://www.tfl.gov.uk/tfl/businessandpartners/syndication/feed.aspx?email=%s&feedid=%s' % (kw['email'], kw['feedid'])
    refresh = 300
    while True:
        try:
            tStart = time.time()
            updated_at = strftime("%d/%m/%y %H:%M:%S")
            #GET DATA
            req = urllib2.Request(url)
            data = urllib2.urlopen(req).read()
            dom = parseString(data.encode("ascii", "ignore"))

            #STORE XML IN DB
            store_tfl_data(cursor, conn, dom, updated_at)

            #GET REFRESH DYNAMICALLY
            refresh = 60 * float(dom.getElementsByTagName('Header')[0].getElementsByTagName('RefreshRate')[0].firstChild.data)
            
            tEnd = time.time()
            remain = refresh - ( tEnd - tStart )
            print "TfL Feed Stored @%s" % updated_at
            print "Sleeping For", remain, "Seconds"
            if remain > 0: time.sleep(remain)
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Error -> %s" % (exceptionValue)
            time.sleep(refresh)

###############################################################################################
########################### Store the tfl feed in the database ################################
###############################################################################################

def store_tfl_data(cursor, conn, dom, updated_at):
    events = dom.getElementsByTagName('roadrunner')[0].getElementsByTagName('rr_event')

    cursor.execute("DELETE FROM tfl")    

    for event in events:
        rrevent = {}
        rrevent['updated_at'] = updated_at
        rrevent['ltisid'] = event.getElementsByTagName("ltisid")[0].firstChild.data
        rrevent['eventstartdate'] = event.getElementsByTagName("eventstartdate")[0].firstChild.data
        rrevent['eventstarttime'] = event.getElementsByTagName("eventstarttime")[0].firstChild.data
        rrevent['eventenddate'] = event.getElementsByTagName("eventenddate")[0].firstChild.data
        rrevent['eventendtime'] = event.getElementsByTagName("eventendtime")[0].firstChild.data
        rrevent['event_type'] = event.getElementsByTagName("event_type")[0].firstChild.data
        rrevent['category'] = event.getElementsByTagName("category")[0].firstChild.data
        rrevent['title'] = event.getElementsByTagName("title")[0].firstChild.data
        rrevent['sector'] = event.getElementsByTagName("sector")[0].firstChild.data
        rrevent['location'] = event.getElementsByTagName("location")[0].firstChild.data
        rrevent['description'] = event.getElementsByTagName("description")[0].firstChild.data
        rrevent['lastmodifiedtime'] = event.getElementsByTagName("lastmodifiedtime")[0].firstChild.data
        rrevent['severity'] = event.getElementsByTagName("severity")[0].firstChild.data
        rrevent['PostCodeStart'] = event.getElementsByTagName("PostCodeStart")[0].firstChild.data
        rrevent['PostCodeEnd'] = event.getElementsByTagName("PostCodeEnd")[0].firstChild.data
        rrevent['remarkDate'] = event.getElementsByTagName("remarkDate")[0].firstChild.data
        rrevent['remarkTime'] = event.getElementsByTagName("remarkTime")[0].firstChild.data
        rrevent['remark'] = event.getElementsByTagName("remark")[0].firstChild.data
        rrevent['gridEasting'] = event.getElementsByTagName("gridEasting")[0].firstChild.data
        rrevent['gridNorthing'] = event.getElementsByTagName("gridNorthing")[0].firstChild.data
        cursor, conn = updaterr(cursor, conn, **rrevent)

    conn.commit()

def updaterr(cursor, conn, **rrevent):
    if rrevent['gridNorthing']!="NULL" and rrevent['gridEasting']!="NULL":
        lon, lat = grid2lonlat(float(rrevent['gridNorthing']), float(rrevent['gridEasting']))
        geoValue = "ST_GeographyFromText('SRID=4326; POINT(%s %s)'))" % (lon, lat)
    else:
        geoValue = "NULL)"
    try:
        queryColumns = "("
        queryValues = " VALUES("

        for key in rrevent:
            rrevent[key] = rrevent[key].replace("'","''").replace(u'\xbf',"")
            queryColumns+="%s," % key
            if(rrevent[key]!='NULL'): queryValues+="'%s'," % rrevent[key]
            else: queryValues+="NULL,"

        queryColumns += "lonlat)"
        query_archive = "INSERT INTO archive" + queryColumns + queryValues + geoValue

        cursor.execute(query_archive)

        query_tfl = "INSERT INTO tfl" + queryColumns + queryValues + geoValue
        cursor.execute(query_tfl)
        return cursor, conn
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        print "Insert failed! -> %s" % (exceptionValue)

###############################################################################################
############# Calculate longitude latitude from national grid coordinates #####################
###############################################################################################

def grid2lonlat(N, E):
    #E, N are the British national grid coordinates - eastings and northings
    a, b = 6377563.396, 6356256.909 #The Airy 180 semi-major and semi-minor axes used for OSGB36 (m)
    F0 = 0.9996012717 #scale factor on the central meridian
    lat0 = 49*pi/180 #Latitude of true origin (radians)
    lon0 = -2*pi/180 #Longtitude of true origin and central meridian (radians)
    N0, E0 = -100000, 400000 #Northing & easting of true origin (m)
    e2 = 1 - (b*b)/(a*a) #eccentricity squared
    n = (a-b)/(a+b)

    #Initialise the iterative variables
    lat,M = lat0, 0

    while N-N0-M >= 0.00001: #Accurate to 0.01mm
        lat = (N-N0-M)/(a*F0) + lat;
        M1 = (1 + n + (5/4)*n**2 + (5/4)*n**3) * (lat-lat0)
        M2 = (3*n + 3*n**2 + (21/8)*n**3) * sin(lat-lat0) * cos(lat+lat0)
        M3 = ((15/8)*n**2 + (15/8)*n**3) * sin(2*(lat-lat0)) * cos(2*(lat+lat0))
        M4 = (35/24)*n**3 * sin(3*(lat-lat0)) * cos(3*(lat+lat0))
        #meridional arc
        M = b * F0 * (M1 - M2 + M3 - M4)

    #transverse radius of curvature    
    nu = a*F0/sqrt(1-e2*sin(lat)**2)

    #meridional radius of curvature
    rho = a*F0*(1-e2)*(1-e2*sin(lat)**2)**(-1.5)
    eta2 = nu/rho-1

    secLat = 1./cos(lat)
    VII = tan(lat)/(2*rho*nu)
    VIII = tan(lat)/(24*rho*nu**3)*(5+3*tan(lat)**2+eta2-9*tan(lat)**2*eta2)
    IX = tan(lat)/(720*rho*nu**5)*(61+90*tan(lat)**2+45*tan(lat)**4)
    X = secLat/nu
    XI = secLat/(6*nu**3)*(nu/rho+2*tan(lat)**2)
    XII = secLat/(120*nu**5)*(5+28*tan(lat)**2+24*tan(lat)**4)
    XIIA = secLat/(5040*nu**7)*(61+662*tan(lat)**2+1320*tan(lat)**4+720*tan(lat)**6)
    dE = E-E0

    #These are on the wrong ellipsoid currently: Airy1830. (Denoted by _1)
    lat_1 = lat - VII*dE**2 + VIII*dE**4 - IX*dE**6
    lon_1 = lon0 + X*dE - XI*dE**3 + XII*dE**5 - XIIA*dE**7

    #Want to convert to the GRS80 ellipsoid.
    #First convert to cartesian from spherical polar coordinates
    H = 0 #Third spherical coord.
    x_1 = (nu/F0 + H)*cos(lat_1)*cos(lon_1)
    y_1 = (nu/F0+ H)*cos(lat_1)*sin(lon_1)
    z_1 = ((1-e2)*nu/F0 +H)*sin(lat_1)

    #Perform Helmut transform (to go between Airy 1830 (_1) and GRS80 (_2))
    s = -20.4894*10**-6 #The scale factor -1
    tx, ty, tz = 446.448, -125.157, + 542.060 #The translations along x,y,z axes respectively
    rxs,rys,rzs = 0.1502, 0.2470, 0.8421 #The rotations along x,y,z respectively, in seconds
    rx, ry, rz = rxs*pi/(180*3600.), rys*pi/(180*3600.), rzs*pi/(180*3600.) #In radians
    x_2 = tx + (1+s)*x_1 + (-rz)*y_1 + (ry)*z_1
    y_2 = ty + (rz)*x_1 + (1+s)*y_1 + (-rx)*z_1
    z_2 = tz + (-ry)*x_1 + (rx)*y_1 + (1+s)*z_1

    #Back to spherical polar coordinates from cartesian
    #Need some of the characteristics of the new ellipsoid
    a_2, b_2 =6378137.000, 6356752.3141 #The GSR80 semi-major and semi-minor axes used for WGS84(m)
    e2_2 = 1- (b_2*b_2)/(a_2*a_2) #The eccentricity of the GRS80 ellipsoid
    p = sqrt(x_2**2 + y_2**2)

    #Lat is obtained by an iterative proceedure:
    lat = atan2(z_2,(p*(1-e2_2))) #Initial value
    latold = 2*pi
    while abs(lat - latold)>10**-16:
        lat, latold = latold, lat
        nu_2 = a_2/sqrt(1-e2_2*sin(latold)**2)
        lat = atan2(z_2+e2_2*nu_2*sin(latold), p)

    #Lon and height are then pretty easy
    lon = atan2(y_2,x_2)
    H = p/cos(lat) - nu_2

    #Convert to degrees
    lat = lat*180/pi
    lon = lon*180/pi

    return lon,lat

if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")

    configSection = "TfL feed"
    email = Config.get(configSection, "email")
    feedid = Config.get(configSection, "feedid")

    # Parse options from the command line
    parser = optparse.OptionParser("usage: %prog [options]")
    parser.add_option('-H','--host',
                    dest='host',
                    default=host,
                    help='The hostname of the DB')
    parser.add_option('-d','--database',
                    dest='database',
                    default=database,
                    help='The name of the DB')
    parser.add_option('-u','--user',
                    dest='user',
                    default=user,
                    help='The username for the DB')
    parser.add_option('-p','--password',
                    dest='password',
                    default=password,
                    help='The password for the DB')
    parser.add_option('-e','--email',
                    dest='email',
                    default=email,
                    help='The email for the TfL feed')
    parser.add_option('-f','--feedid',
                    dest='feedid',
                    default=feedid,
                    help='The for the TfL feed')
    (options, args) = parser.parse_args()

    kw = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    sys.exit(main(**kw))

