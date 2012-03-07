package uk.ac.ic.doc.t4t.common.services.data;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.joda.time.DateTime;
import org.joda.time.Days;
import org.joda.time.Hours;
import org.joda.time.Minutes;
import org.joda.time.Seconds;

import android.util.Log;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventdetails.TweetTIDComparator;
import uk.ac.ic.doc.t4t.eventlist.EventLocationComparator;

public class TweetPostProcessor {
	private static final String TAG = TweetPostProcessor.class.getSimpleName();
	
	public final static long SECOND_MILLIS = 1000;
	public final static long MINUTE_MILLIS = SECOND_MILLIS * 60;
	public final static long HOUR_MILLIS = MINUTE_MILLIS * 60;
	public final static long DAY_MILLIS = HOUR_MILLIS * 24;
	
	private SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"); 

	public List<TweetItem> processTweets(List<TweetItem> tweets){
		
		calculateTweetAge(tweets);
		Collections.sort(tweets, new TweetTIDComparator());
		
		return tweets;
	}

	private void calculateTweetAge(List<TweetItem> tweets) {
		
		DateTime currentDateTime = new DateTime();
		
		Log.i(TAG, "Current time " + currentDateTime);
		for (TweetItem tweet : tweets){
			
			Date tweetDate;
			try {
				
				tweetDate = format.parse(tweet.getCreatedAt());
				DateTime tweetDateTime = new DateTime(tweetDate);

				Days d = Days.daysBetween(tweetDateTime, currentDateTime);
				Hours h = Hours.hoursBetween(tweetDateTime, currentDateTime);
				Minutes m = Minutes.minutesBetween(tweetDateTime, currentDateTime);
				Seconds s = Seconds.secondsBetween(tweetDateTime, currentDateTime);

				if (d.getDays() > 0){
					tweet.setTweetAge(d.getDays()+" days");
				} else if (h.getHours() > 0){
					tweet.setTweetAge(h.getHours()+" hrs");
				} else if (m.getMinutes() > 0){
					tweet.setTweetAge(m.getMinutes() + " min");
				} else if (s.getSeconds() > 0){
					tweet.setTweetAge(s.getSeconds() + " sec");
				}

			} catch (ParseException e) {
				Log.e(TAG, "Error parsing date for " + tweet.getCreatedAt());
			}  
		}
		
	}
	
}
