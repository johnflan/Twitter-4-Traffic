import twitter
import time
from datetime import datetime
DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

if __name__ == '__main__':
    import sys
    sys.path.append('..')

from pygraph.simulation.infoflow_config import QUIET, STDOUTPUT, VERBOSE, DEBUG
from data_io.mysqldb_wrapper import make_connection
from data_io.mysqldb_wrapper import select_from_sql_table
from data_io.mysqldb_wrapper import insert_into_sql_table
from data_io.mysqldb_wrapper import update_sql_table
from data_io.mysqldb_wrapper import get_single_selection

####  Twitter Rate Limiting ####
class SuppressedCallException(Exception ):
    def __init__(self, value ):
        self.value = value
    def __str__(self ):
        return repr(self.value)

class RateLimiter(object ):
    """
    Provides a subset of the twitter.Api methods with rate limiting. Only good for single process/thread connections to the api.

    For a list of methdods wrapped see the class attributes readmethods and writemethods.

    For documentation, see the twitter.Api class documentation.
    """
    readmethods = [ 'FilterPublicTimeline',
                    'GetUser',
                    'GetDirectMessages',
                    'GetFavorites',
                    'GetFeatured',
                    'GetFollowerIDs',
                    'GetFollowers',
                    'GetFriendIDs',
                    'GetFriends',
                    'GetFriendsTimeline',
                    'GetLists',
                    'GetMentions',
                    'GetPublicTimeline',
                    'GetReplies',
                    'GetRetweets',
                    'GetSearch',
                    'GetStatus',
                    'GetSubscriptions',
                    'GetTrendsCurrent',
                    'GetTrendsDaily',
                    'GetTrendsWeekly',
                    'GetUser',
                    'GetUserByEmail',
                    'GetUserRetweets',
                    'GetUserTimeline',
                    'MaximumHitFrequency',
                    'UsersLookup',
                    'UsersSearch'
                    ]
    # do we need write methods?
    writemethods = []
    # initializing rate limiting variable 
    def __init__(self,api,verbosity=STDOUTPUT ):
        self.max_calls = 0  # number of allowed calls in one hour : the quota
        self.calls_left = 0  # what is left in the quota
        self.t_end = 0 # end time of an one-hour period
        self.api = api
        for methodname in self.readmethods+self.writemethods:
            self.WrapMethod(methodname)
            self.WaitToMethod(methodname)
            self.FreqLimitMethod(methodname)
        self.GetTwitterRateLimit(api=self.api)
        self.timefrom = None
        self.verbosity = verbosity

    def GetTwitterRateLimit(self,api=None ):
        """
        refresh the number of calls left, max calls and refresh time.
        """
        if api is None:
            api = self.api
        # XXX could be a private method.
        rl = api.GetRateLimitStatus()
        self.calls_left = rl['remaining_hits']
        self.max_calls = rl['hourly_limit']
        self.t_end = rl['reset_time_in_seconds']


    def TwitterRateLimiting(self,callingmethodname=None ):
        """
        Keeps track of the call limits. If broken then
        throws exception.
        """
        t_left = self.t_end - time.time()
        if t_left >= 0 :
            if self.calls_left < 1 :
                #
                    #time.sleep(t_left + 1)
                    # XXX is this a better way than just sleeping?
                    # throws an exception, and this is caught in wrapped method,
                    # wrapped method returns nothing when suppressed but sets attribute
                    # self.suppressed_last_call to True.
                    # This way the thread isn't caught sleeping forever.
                    # I also create WaitTo... methods that wait for this.
                    raise SuppressedCallException('Suppressed method:' + callingmethodname)
            else:
                #
                self.calls_left -= 1
        else:
            #
            self.GetTwitterRateLimit()

    def SleepItOff(self,call_threshold=1 ):
        """
        Conditionally sleeps off time delay, until limit refreshed
        """
        if self.calls_left < call_threshold:
            accum = 1
            while True :
                #
                t_left = self.t_end - time.time()
                if t_left >= 0 :
                    print "Sleeping for %r seconds" % t_left
                    time.sleep(max(t_left + 1,accum))
                else :
                    break
                accum = min(16,2*accum) # we want to have an increasing delay for when clocks are out
            self.GetTwitterRateLimit()

    def WrapMethod(self,methodname ):
        """
        Promotes methods from the underlying api to this wrapping class
        """
        method = getattr(self.api,methodname)
        def wrappedmethod(*args,**kwargs ):
            try:
                self.TwitterRateLimiting(methodname)
            except:
                self.suppressed_last_call = True
                return None
            self.suppressed_last_call = False
            return method(*args,**kwargs)
        setattr(self,methodname,wrappedmethod)

    def WaitToMethod(self,methodname ):
        """
        Alternative versions of methods, which sleep until able to call
        """
        method = getattr(self.api,methodname)
        def waittomethod(*args,**kwargs ):
            while True:
                try:
                    self.TwitterRateLimiting(methodname)
                    break
                except:
                    self.SleepItOff()
            self.suppressed_last_call = False
            return method(*args,**kwargs)
        setattr(self,'WaitTo'+methodname,waittomethod)

    def FreqLimitMethod(self,methodname ):
        """
        Alternative versions of methods, which wait the appropriate length before calling
        Twitter api may throttle us if we try calling repeatedly but within our limit.
        """
        method = getattr(self.api,methodname)
        def freqlimitmethod(*args,**kwargs ):
            if self.verbosity >= DEBUG:
                print "[debug] In FreqLimit"+methodname
            if self.timefrom == None:
                self.timefrom = time.time() - self.MaximumHitFrequency()
            waittill = self.timefrom + self.MaximumHitFrequency()
            now = time.time()
            if now > waittill:
                pass
            else:
                if self.verbosity >= STDOUTPUT:
                    print "Sleeping for "+ str(waittill-now)+ " seconds"
                time.sleep(waittill-now)
                if self.verbosity >= STDOUTPUT:
                    print "Waking up"
            res = method(*args,**kwargs)
            self.timefrom = time.time()
            return res
        setattr(self,'FreqLimit'+methodname,freqlimitmethod)

def GetRateLimiter(
    consumer_key    = 'XXXXXXXXXXXXXXXXXXXX',
    consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_token_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    **kwargs
    ):

    api = twitter.Api(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token_key=access_token_key,
                        access_token_secret=access_token_secret)
    rlapi=RateLimiter(api,verbosity=kwargs.get('verbosity',STDOUTPUT))
    return rlapi


