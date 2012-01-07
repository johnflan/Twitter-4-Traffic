"""
Periodically samples tfl disruptions feed. Lots of hardcoding in this module.
Samples every 5 minutes and copies to temporary file. Checks datestamp and renames file to reflect this.
If the temporary file is empty (as sometimes happens). It will try again a number of times.
Example call:
$ python tfltrafficfeedreader.py
"""
import os
import sys
import re
import sqlite3
from sqlite3 import OperationalError
import time
import datetime
import urllib2
import ConfigParser
from copy import copy
from logging import  FATAL, ERROR, WARNING, INFO, DEBUG
from xml.dom.minidom import parseString

# my stuff
#from uktwaffic import DATETIME_STRING_FORMAT, DT_FORMAT_TIMESTAMP
# canonical format
DT_FORMAT_CANON = '%Y-%m-%d %H:%M:%S'
# wierd tfl format - like this 2011-10-24T1116
DT_FORMAT_UPDATE = '%Y-%m-%dT%H%M'
# my timestamp format
DT_FORMAT_TIMESTAMP = '%Y%m%d%H%M%S'

FEED_LOCATION = ""

# reading and writing datetime objects from/to strings
def strptime(dtstr,format=DT_FORMAT_CANON):
    try:
        return datetime.datetime.strptime(dtstr, format)
    except:
        return None

def strftime(dtobj,format=DT_FORMAT_TIMESTAMP):
    return datetime.datetime.strftime(dtobj, format)

###
###XXX tested seems fine
###

def get_dom(xmlfname):
    # Read file in
    xmlfile = open(xmlfname,'r')
    data = xmlfile.read()
    xmlfile.close()
    # Parse file into dom object
    dom = parseString(data)
    return dom

###
###XXX tested seems fine
###

def get_publish_datetime(dom):
    # Extract XML root data
    name = dom.getElementsByTagName('name')[0].firstChild.data
    descrip = dom.getElementsByTagName('description')[0].firstChild.data
    # Extract XML header data
    header = dom.getElementsByTagName('Header')[0]
    identifier = header.getElementsByTagName('Identifier')[0].firstChild.data
    owner = header.getElementsByTagName('Owner')[0].firstChild.data
    publishdtnode = header.getElementsByTagName('PublishDateTime')[0]
    publishdtstr = publishdtnode.getAttribute('canonical')
#    publishdtstr = header.getElementsByTagName('PublishDateTime')[0].firstChild.data
    return strptime(publishdtstr,format=DT_FORMAT_CANON)

###
###XXX tested seems fine
###

def get_update_datetime(dom):
    rr =  dom.getElementsByTagName('roadrunner')[0]
    updatedtstr = rr.getAttribute('updatetime')
    return strptime(updatedtstr,format=DT_FORMAT_UPDATE)


###
###XXX tested seems fine
###

def allrrevents(dom):
    update_at = get_update_datetime(dom)
    # Extract XML events data
    events = dom.getElementsByTagName('roadrunner')[0].getElementsByTagName('rr_event')
    for event in events:
        ltisid = getattr(event.getElementsByTagName("ltisid")[0].firstChild,"data",None)
        eventstartdate = getattr(event.getElementsByTagName("eventstartdate")[0].firstChild,"data",None)
        eventstarttime = getattr(event.getElementsByTagName("eventstarttime")[0].firstChild,"data",None)
        eventstart = strptime(eventstartdate+'T'+eventstarttime,format=DT_FORMAT_UPDATE)
        eventenddate = getattr(event.getElementsByTagName("eventenddate")[0].firstChild,"data",None)
        eventendtime = getattr(event.getElementsByTagName("eventendtime")[0].firstChild,"data",None)
        eventend = strptime(eventenddate+'T'+eventendtime,format=DT_FORMAT_UPDATE)
        event_type = getattr(event.getElementsByTagName("event_type")[0].firstChild,"data",None)
        category = getattr(event.getElementsByTagName("category")[0].firstChild,"data",None)
        title = getattr(event.getElementsByTagName("title")[0].firstChild,"data",None)
        sector = getattr(event.getElementsByTagName("sector")[0].firstChild,"data",None)
        location = getattr(event.getElementsByTagName("location")[0].firstChild,"data",None)
        description = getattr(event.getElementsByTagName("description")[0].firstChild,"data",None)
        lastmodifiedtime = getattr(event.getElementsByTagName("lastmodifiedtime")[0].firstChild,"data",None)
        severity = getattr(event.getElementsByTagName("severity")[0].firstChild,"data",None)
        PostCodeStart = getattr(event.getElementsByTagName("PostCodeStart")[0].firstChild,"data",None)
        PostCodeEnd = getattr(event.getElementsByTagName("PostCodeEnd")[0].firstChild,"data",None)
        remarkDate = getattr(event.getElementsByTagName("remarkDate")[0].firstChild,"data",None)
        remarkTime = getattr(event.getElementsByTagName("remarkTime")[0].firstChild,"data",None)
        remark_at = strptime(remarkDate+'T'+remarkTime,format=DT_FORMAT_UPDATE)
        remark = getattr(event.getElementsByTagName("remark")[0].firstChild,"data",None)
        gridEasting = getattr(event.getElementsByTagName("gridEasting")[0].firstChild,"data",None)
        gridNorthing = getattr(event.getElementsByTagName("gridNorthing")[0].firstChild,"data",None)

        yield ( update_at,
			    ltisid,
			    eventstart,
			    eventend,
			    event_type,
			    category,
			    title,
			    sector,
			    location,
			    description,
			    lastmodifiedtime,
			    severity,
			    PostCodeStart,
			    PostCodeEnd,
			    remark_at,
			    remark,
			    gridEasting,
			    gridNorthing )

###
###TODO Changes still to test
###

def process_rrevents(conn,cursor,dom):
    """
    Processes all road runner events in the tfl xml and inserts into sqlite file.

    """
    for rrevent in allrrevents(dom):
        print rrevent
        written = False
        tries = 0
        while True:
            try:
                cursor.execute('INSERT OR IGNORE INTO disruptions('+ \
                'update_at, ltisid, eventstart, eventend, event_type, category, title,' + \
                'sector, location, description, lastmodifiedtime, severity, PostCodeStart,' + \
                'PostCodeEnd, remark_at, remark, gridEasting, gridNorthing)' + \
                'VALUES(?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', rrevent)
                conn.commit()
                written = True
            except OperationalError, oe:
                if tries < 5:
                    print "Failed to write with error", oe, 'Trying again...'
                    tries += 1
                else:
                    raise
            if written:
                break

###
###TODO changes still to make/test
###

def create_database(*args,**kwds):
    sqlfname = kwds['sqlfname']
    datadir = kwds['datadir']
    conn = sqlite3.connect(datadir+os.sep+slqfname)
    cursor = conn.cursor()
    created = False
    tries = 0
    while True:
        try:
            # (ltisid, eventstart, eventend, event_type, category, title, sector, location, description, lastmodifiedtime, severity, PostCodeStart, PostCodeEnd, remark_at, remark, gridEasting, gridNorthing )
            cursor.execute('CREATE TABLE IF NOT EXISTS disruptions(' + \
            'update_at DATETIME, ltisid INTEGER, eventstart DATETIME,' + \
            'eventend DATETIME, event_type INTEGER, category TEXT, title TEXT,' + \
            'sector TEXT, location TEXT, description TEXT, lastmodifiedtime DATETIME,' + \
            'severity TEXT, PostCodeStart TEXT, PostCodeEnd TEXT, remark_at DATETIME,' + \
            'remark TEXT, gridEasting INTEGER, gridNorthing INTEGER, UNIQUE (update_at,ltisid))')
            conn.commit()
            cursor.execute('CREATE INDEX IF NOT EXISTS update_at_idx ON disruptions(update_at)')
            conn.commit()
            cursor.execute('CREATE INDEX IF NOT EXISTS ltisid_idx ON disruptions(ltisid)')
            conn.commit()
        except OperationalError, oe:
            if tries < 5:
                print "Failed to create tables with error", oe, "Trying again..."
                tries += 1
            else:
                raise
        if created:
            break


def incorporate_files(*args,**kwds):
    datadir = '/data/ml4t/tfl'
    #TODO we either want to pass in the earliest timestamp or get it from the database itself
    #TODO it may also be worth 
    earliesttimestamp = strptime('20111028012100',format=DT_FORMAT_TIMESTAMP)
    for fname in os.listdir(datadir):
        print fname
        if fname.find('disruptions') >= 0 and fname.find('.xml') >= 0:
            xmlfname = datadir+os.sep+fname
            print xmlfname
            processthis = False
            try:
                dom = get_dom(xmlfname)
                filetimestampstr = fname.split('disruptions')[-1].split('.')[0]
                filetimestamp = strptime(filetimestampstr,format=DT_FORMAT_TIMESTAMP)
                if filetimestamp > earliesttimestamp:   processthis = True
            except:
                print "This may not be one worth keeping"
            if processthis:
                publishdt = get_publish_datetime(dom)
                updatedt = get_update_datetime(dom)
                print updatedt
                process_rrevents(conn,cursor,dom)
                if fname.find('tfldisruptions') >= 0:
                    newxmlfname = datadir+os.sep+ 'disruptions' + strftime(get_update_datetime(dom)) + '.xml'
                    os.rename(xmlfname,newxmlfname)
            else:
                print 'Ignoring'


###
###TODO Changes still to test
###

def periodically_sample_feed(*args,**kwds):
    verbosity = kwds['verbosity']
    datadir = kwds['datadir']
    tries = kwds['tries']
    feed_location = kwds['feed_location']
    print "[debug] in periodically sample feed: " + feed_location
    # this is the feed address
    #XXX This loc no longer points to a real feed. YOu will need to register an email address and ip address foryour own machine.
    #loc = 'http://www.tfl.gov.uk/tfl/businessandpartners/syndication/feed.aspx?email=youremail and id goes here'
    durn = datetime.timedelta(minutes=5)
    while True:
        triesleft = tries
        filesize = 0
        newfeedtime = datetime.datetime.now()
        lastfeedcollected = newfeedtime
        while filesize == 0 and triesleft > 0:
            if triesleft < tries:
                print "File downloaded is empty, trying again in 10 seconds..."
                time.sleep(10)
                print "...trying again."
            # Get the newly published feed
            if verbosity <= INFO:   print "Requesting new feed..."
            req = urllib2.Request(feed_location)
            f = urllib2.urlopen(req)
            tmpfname = os.path.join(datadir,'tempdisruptions.xml')
            tmpfile = open(tmpfname,'w')
            tmpfile.writelines(f.readlines())
            tmpfile.close()
            filesize = os.path.getsize(tmpfname)
            triesleft -= 1

        if filesize > 0:
            # read the update date to rename the file appropriately.
            dom = get_dom(tmpfname)
            update_at = get_update_datetime(dom)
            update_at_str = strftime(update_at,DT_FORMAT_TIMESTAMP)
            ofname = datadir + os.sep + 'tfldisruptions'+update_at_str+'.xml'
            if verbosity <= INFO:   print "Writing to %s..." % ofname
            os.rename(tmpfname,ofname)
        else:
            lastfeedcollected = newfeedtime
            print "After %d tries the feed is still empty, so ignoring." % tries

        now = datetime.datetime.now()
        while (now - lastfeedcollected) < durn:
            remains = max((durn - (now-lastfeedcollected)).seconds,0)+10
            if verbosity <= 10:
                print "[debug] Still some %d seconds till next lastfeedcollected" % remains
                print "[debug] Sleeping..."
            # feeds are published 5 seconds after their update time, so this is to ensure we get the right one first time (although code is robust anyway)
            time.sleep(remains)
            now = datetime.datetime.now()


###
###
###

def main(*args,**kwds):
	Config = ConfigParser.ConfigParser()
	Config.read("../t4t_credentials.txt")
	feed_location = Config.get("Transport for London", "tfl_traffic_disruptions")
	if feed_location == "":
		print "Could not load disruptions feed from config file"
		sys.exit(0)
	kwds['feed_location'] = feed_location
	periodically_sample_feed(*args,**kwds)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-v','--verbosity',
                        dest='verbosity',
                        default=20,
                        type=int,
                        help='The verbosity level of the output 50 (FATAL), 40 (ERROR), 30 (WARNING), 20 (INFO), 10 (DEBUG)')
    parser.add_option('-d','--datadir',
                        dest='datadir',
                        default='/data/ml4t/tfl',
                        help='The directory in which to store the data')
    parser.add_option('--sqlfname',
                        dest='sqlfname',
                        default='disruptions.sqlite',
                        help='The sqlite file for the disruptions')
    parser.add_option('--tries',
                        dest='tries',
                        default=10,
                        type=int,
                        help='Number of tries for each feed attempt.')
    (options, args) = parser.parse_args()
    kwds = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    verbosity = kwds['verbosity']
    if verbosity not in [ FATAL, ERROR, WARNING, INFO, DEBUG ]:
        raise ValueError, 'Verbosity level is not recognised. You chose %r but limited to 50 (FATAL), 40 (ERROR), 30 (WARNING), 20 (INFO), or 10 (DEBUG).' % verbosity
    if verbosity <= INFO:
        print "args",args
        print "kwds",kwds
    main(*args,**kwds)

