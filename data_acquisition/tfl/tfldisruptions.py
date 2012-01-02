"""
Module to manage disruptions database

Takes tfldisruption xml files and insert details into database. Example
$ python tfldisruptions.py --xmlstem tfl
Also, reads database and extracts lifecycle of disruptions (those with a severity that becomes Serious or Severe at some point in their lifecycle).
$ python tfldisruptions.py --lifecycles --tfldb /data/ml4t/tfl/disruptions_copy.sqlite
"""

import os
import sys
import re
import sqlite3
from sqlite3 import OperationalError
import time
import datetime

from logging import  FATAL, ERROR, WARNING, INFO, DEBUG
from xml.dom.minidom import parseString
# like this 2011-10-24 11:16:05
DT_FORMAT_CANON = '%Y-%m-%d %H:%M:%S'
# like this 2011-10-24T1116
DT_FORMAT_UPDATE = '%Y-%m-%dT%H%M'
DT_FORMAT_TIMESTAMP = '%Y%m%d%H%M%S'

DT_FORMAT_WKDY = '%A %d %b'

# reading and writing datetime objects from/to strings
def strptime(dtstr,format=DT_FORMAT_CANON):
    try:
        return datetime.datetime.strptime(dtstr, format)
    except:
        return None

def strftime(dtobj,format=DT_FORMAT_TIMESTAMP):
    return datetime.datetime.strftime(dtobj, format)

###
### xml feed parsing helper files
###


def get_dom(xmlfname):
    # Read file in
    file = open(xmlfname,'r')
    data = file.read()
    file.close()
     
    # Parse file into dom object
    dom = parseString(data)
    return dom

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

def get_update_datetime(dom):
    rr =  dom.getElementsByTagName('roadrunner')[0]
    updatedtstr = rr.getAttribute('updatetime')
    return strptime(updatedtstr,format=DT_FORMAT_UPDATE)


def allrrevents(dom):
    """
    Creates a generator for all the events in the dom.
    """
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

def process_rrevents(conn,cursor,dom):
    verbosity = WARNING
    for rrevent in allrrevents(dom):
        if verbosity <= INFO:
            print rrevent
        written = False
        tries = 0
        while True:
            try:
                cursor.execute('INSERT OR IGNORE INTO disruptions(update_at, ltisid , eventstart , eventend , event_type , category , title , sector , location , description , lastmodifiedtime , severity , PostCodeStart , PostCodeEnd , remark_at , remark , gridEasting , gridNorthing ) VALUES(?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', rrevent)
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
### digesting database methods
###

def extract_lifecycles(**kwargs):
    ltisidbatch = 5000
    verbosity = kwargs['verbosity']
    tflconn,tflcursor = connect_tfldb(**kwargs)
    digestconn,digestcursor = connect_digestdb(**kwargs)
    minltisid = kwargs['minltisid']

    finished = False
    while not finished:
        finished = True # if set to false again then we reiterate
        t1 = datetime.datetime.now()
        tflcursor.execute("SELECT ltisid FROM disruptions WHERE ltisid > ? AND (severity = 'Serious' OR severity = 'Severe') GROUP BY ltisid ORDER BY ltisid LIMIT ?", (minltisid,ltisidbatch) )
        fetchedids = tflcursor.fetchall()
        tflconn.commit()
        if verbosity <= INFO:
            print "SQL Request took %r seconds " % ((datetime.datetime.now()-t1).seconds)
        for (ltisid,) in fetchedids:
            if verbosity <= INFO:
                print "Processing event: %r of type %r" % (ltisid,type(ltisid))
            finished = False # some results so we must reiterate
            minltisid = ltisid
            lastseverity = None
            occurrences = dict()
            tflcursor.execute('SELECT update_at, severity FROM disruptions WHERE ltisid = '+str(ltisid)+' ORDER BY update_at')
            for update_at, severity in tflcursor:
                if lastseverity != severity:
                    statuschange = True
                    occurrence = occurrences.get(severity,0)+1
                    occurrences[severity] = occurrence
                    # if we have processed a previous severity impact for this ltisid, then we need to cap it off
                    if lastseverity is not None:
                        digestcursor.execute('UPDATE impact SET past = ? WHERE ltisid = ? AND severity = ? AND occurrence = ?' , (update_at,ltisid,lastseverity,lastoccurrence) )
                        digestconn.commit()
                    ##print "update_at", update_at
                    ##print "(update_at,ltisid,severity,occurrence) ",(update_at,ltisid,severity,occurrence) 
                    digestcursor.execute('INSERT INTO impact(first,ltisid,severity,occurrence) VALUES(?,?,?,?)' , (update_at,ltisid,severity,occurrence) )
                    digestconn.commit()
                    if verbosity <= DEBUG:
                        print "\tseverity %r registered at %r (occ. %r)" % (severity,update_at,occurrence)

                else:                
                    statuschange = False
                    occurrence = occurrences[severity]

                lastseverity = severity
                lastupdate_at = update_at
                lastoccurrence = occurrence
            # the last status change for some ltisid has no past set, so we assume this is 5 minutes past the last recorded entry.
            assumed_update_at = strptime(lastupdate_at,format=DT_FORMAT_CANON)+datetime.timedelta(minutes=5)
            ##print "assumed_update_at", assumed_update_at
            digestcursor.execute('UPDATE impact SET past = ? WHERE ltisid = ? AND severity = ? AND occurrence = ?' , (assumed_update_at,ltisid,lastseverity,lastoccurrence) )
            digestconn.commit()
                

    

###
### database management
###

def connect_tfldb(**kwargs):
    tfldb = kwargs['tfldb']
    conn = sqlite3.connect(tfldb)
    cursor = conn.cursor()
    # (ltisid , eventstart , eventend , event_type , category , title , sector , location , description , lastmodifiedtime , severity , PostCodeStart , PostCodeEnd , remark_at , remark , gridEasting , gridNorthing )
    cursor.execute('CREATE TABLE IF NOT EXISTS disruptions(update_at DATETIME, ltisid INTEGER, eventstart DATETIME, eventend DATETIME, event_type INTEGER, category TEXT, title TEXT, sector TEXT, location TEXT, description TEXT, lastmodifiedtime DATETIME, severity TEXT, PostCodeStart TEXT, PostCodeEnd TEXT, remark_at DATETIME, remark TEXT, gridEasting INTEGER, gridNorthing INTEGER, UNIQUE (update_at,ltisid))')
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS update_at_idx ON disruptions(update_at)')
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS ltisid_idx ON disruptions(ltisid)')
    conn.commit()
    return conn,cursor

##

def connect_digestdb(**kwargs):
    """
    Creates a digest database, with the necessary tables, currently these are:
    impact: contains the severity lifecycle of each event that becomes at least
    serious. For each such ltisid and for each contiguous period of severity 
    classification, we record the first and past timestamp where first is the
    time of the first update (created_at) at which the event gets a new
    classification, past is the time of the first update at which the event is
    no longer classified as such). occurrence is the number of times previously
    that this ltisid has had this classification.
    """
    digestdb = kwargs['digestdb']
    conn = sqlite3.connect(digestdb)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS impact(first DATETIME, past DATETIME, ltisid INTEGER, severity TEXT, occurrence INTEGER, UNIQUE (ltisid,severity,occurrence))')
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS ltisidimpact_idx ON impact(ltisid)')
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS firstimpact_idx ON impact(first)')
    conn.commit()
    cursor.execute('CREATE INDEX IF NOT EXISTS pastimpact_idx ON impact(past)')
    conn.commit()
    return conn,cursor


###
###
###


def main(*args,**kwargs):

    lifecycles = kwargs['lifecycles']
    if lifecycles == True:
        extract_lifecycles(**kwargs)
        return

    conn,cursor = connect_tfldb(**kwargs)
    xmlstem = kwargs['xmlstem']
    xmldir = '/data/ml4t/tfl'
    if 'startdt' in kwargs:
        startdt = kwargs['startdt']
        earliesttimestamp = strptime(startdt,format=DT_FORMAT_CANON)
    else:
        earliesttimestamp = None
    if 'enddt' in kwargs:
        enddt = kwargs['enddt']
        latesttimestamp = strptime(enddt,format=DT_FORMAT_CANON)
    else:
        latesttimestamp = None

    for fname in getfiles(xmldir,matches=xmlstem+'.*\.xml'):
        print fname
        xmlfname = os.path.join(xmldir,fname)
        print xmlfname
        processthis = False
        try:
            dom = get_dom(xmlfname)
            filetimestampstr = fname.split('disruptions')[-1].split('.')[0]
            filetimestamp = strptime(filetimestampstr,format=DT_FORMAT_TIMESTAMP)
            tooearly,toolate = False,False
            if earliesttimestamp is not None and filetimestamp < earliesttimestamp:   tooearly = True
            if latesttimestamp is not None and filetimestamp > latesttimestamp:   toolate = True
            if not (tooearly or toolate):   processthis = True
        except:
            print "This may not be one worth keeping"
        if processthis:
            publishdt = get_publish_datetime(dom)
            updatedt = get_update_datetime(dom)
            print updatedt
            process_rrevents(conn,cursor,dom)
            if fname.find('tfldisruptions') >= 0:
                newxmlfname = xmldir+os.sep+ 'disruptions' + strftime(get_update_datetime(dom)) + '.xml'
                os.rename(xmlfname,newxmlfname)
##            else:
##                print 'Ignoring'
#                cursor.execute('INSERT OR IGNORE INTO reports(published_at ) VALUES(?)', (updatedt,))
#                conn.commit()

###
###
###

def getfiles(dirpath,matches=None):
    """
    Get time ordered list of files in a directory, filtered by the regex filter 'matches'
    """
    if matches is not None:
        a = [s for s in os.listdir(dirpath)
             if re.match(matches,s) is not None and os.path.isfile(os.path.join(dirpath, s))]
    else:
        a = [s for s in os.listdir(dirpath)
             if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    return a

###
###
###

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--tfldb',
                        dest='tfldb',
                        default='/data/ml4t/tfl/disruptions.sqlite',
                        help='The input sql file for tfl disruptions')
    parser.add_option('--digestdb',
                        dest='digestdb',
                        default='/data/ml4t/tfl/digest.sqlite',
                        help='The sqlite3 database file with the digested disruptions information')
    parser.add_option('--minltisid',
                        dest='minltisid',
                        default=0,
                        help='The minimum ltisid to begin searching at (for digest - severity lifecycle.)')
    parser.add_option('--xmldir',
                        dest='xmldir',
                        default='/data/ml4t/tfl',
                        help='The directory with the xml data feeds')
    parser.add_option('--startdt',
                        dest='startdt',
                        default=None,
                        help='The date time to start at, else use sqlite file minimum')
    parser.add_option('--enddt',
                        dest='enddt',
                        default=None,
                        help='The date time to end at, else use sqlite file minimum')
    parser.add_option('--laterthandb',
                        dest='laterthandb',
                        default=None,
                        help='Inspect database and only include files with timestamps newer than latest timestamp in database')
    parser.add_option('--xmlstem',
                        dest='xmlstem',
                        default='tfldisruptions',
                        help='The xml file prefix/stem that needs to be matched')
    parser.add_option('--lifecycles',
                        dest='lifecycles',
                        default='False',
                        action='store_true',
                        help='Extract all events that are not moderate for their entire life and create new lifecycles table')
    parser.add_option('--destructive',
                        dest='destructive',
                        default='False',
                        action='store_true',
                        help='Destroy the original table as you go for speed up.')


    parser.add_option('-v', '--verbosity',
                        dest='verbosity', 
                        default=WARNING, 
                        type=int,
                        help='Set the verbosity')


    (options, args) = parser.parse_args()
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    print "args",args
    print "kwargs",kwargs
    main(*args,**kwargs)

