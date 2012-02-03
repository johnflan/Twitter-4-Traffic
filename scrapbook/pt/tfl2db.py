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
			updated_at = strftime("%y/%m/%d %H:%M:%S")
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
	a = 6377563.396
	b = 6356256.909
	e2 = (a**2 - b**2) / a**2
	N0 = -100000
	E0 = 400000

	F0 = 0.9996012717
	f0 = 49 * pi / 180
	l0 = -2 * pi / 180
	
	n = ( a - b ) / ( a + b )
	
	M = 0
	f = f0
	while True:
		f = ( N-N0-M ) / ( a * F0 ) + f
		M1 = ( 1 + n + 5/4 * n**2 + 5/4 * n**3) * ( f - f0 )
		M2 = (3 * n + 3 * n**2 + 21/8 * n**3) * sin(f-f0) * cos(f+f0)
		M3 = (15/8 * n**2 + 15/8 * n**3) * sin(2 * (f-f0)) * cos(2*(f+f0))
		M4 = 35/24 * n**3 * sin(3*(f-f0))*cos(3*(f+f0))
		M = b * F0 * (M1 - M2 + M3 - M4)
		if abs(N-N0-M) >= 0.00001: break
		
	v = a * F0 * ( 1 - e2 * (sin(f))**2 )**(-0.5)
	p = a * F0 * ( 1 - e2 ) * ( 1 - e2 * (sin(f))**2 )**(-1.5)
	h2 = v / p - 1
	
	secf = 1 / cos(f)
	tanf = tan(f)
	
	VII = tanf / ( 2 * p * v )
	VIII = tanf / ( 24 * p * v**3 ) * ( 5 + 3 * tanf**2 + h2 - 9 * tanf**2 * h2 )
	IX = tanf / ( 720 * p * v**5 ) * ( 61 + 90 * tanf**2 + 45 * tanf**4 )
	X = secf / v
	XI = secf / ( 6 * v**3 ) * ( v / p + 2 * tan(f)**2 )
	XII = secf / ( 120 * v**5 ) * ( 5 + 28 * tan(f)**2 + 24 * tanf**4 )
	XIIA = secf / ( 5040 * v**7 ) * ( 61 + 662 * tan(f)**2 + 1320 * tanf**4 + 720 * tanf**6 )

	lnew = l0 + X * (E-E0) - XI * (E-E0)**3 + XII * (E-E0)**5 - XIIA * (E-E0)**7
	fnew = f - VII * (E-E0)**2 + VIII * (E-E0)**4 - IX * (E-E0)**6
	# lnew = longitude,  fnew = latitude
	return lnew*180/pi, fnew*180/pi

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

