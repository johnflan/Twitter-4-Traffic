package uk.ac.ic.doc.t4t.common.services.data;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.content.Context;
import android.location.Location;
import android.location.LocationManager;
import android.util.Log;

import uk.ac.ic.doc.t4t.common.services.DataMgr;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventlist.EventItem;

public class JSONParser {
	
	private final static String TAG = JSONParser.class.getSimpleName();
	
	//Disruption event parameters
	private final static String EVENT_ID = "eventID";
	private final static String EVENT_START_DATE = "eventstartdate";
	private final static String EVENT_START_TIME = "eventstarttime";
	private final static String EVENT_END_DATE = "eventenddate";
	private final static String EVENT_END_TIME = "eventendtime";
	private final static String EVENT_TYPE = "event_type";
	private final static String CATEGORY = "category";
	private final static String TITLE = "title";
	private final static String SECTOR = "sector";
	private final static String LOCATION = "location";
	private final static String DESCRIPTION = "description";
	private final static String LAST_MODIFIED_TIME = "lastmodifiedtime";
	private final static String SEVERITY = "severity";
	private final static String POST_CODE_START = "PostCodeStart";
	private final static String POST_CODE_END = "PostCodeEnd";
	private final static String REMARK_DATE = "remarkDate";
	private final static String REMARK_TIME = "remarkTime";
	private final static String REMARK = "remark";
	private final static String LATITUDE = "lat";
	private final static String LONGITUDE = "lon";
	
	//Tweet parameters
	private final static String TWEET_ID = "tweetID";
	private final static String USER_NAME = "uname";
	private final static String CREATED_AT = "created_at";
	private final static String ACCOUNT_LOCATION = "location";
	private final static String MESSAGE_TEXT = "text";
	private final static String TWEET_LATITUDE = "lat";
	private final static String TWEET_LONGITUDE = "long";
	
	private LocationManager locationManager;
	private Context context;
	
	public JSONParser(Context context){
		this.context = context;
	}
	
	public List<EventItem> parseDisruptionEvents(String responseStr){
		if ( responseStr == null )
			return null;
		
		//Log.i(TAG, "Response: " + responseStr);
		
		JSONObject response = null;
		try {
			response = new JSONObject( responseStr );
		} catch (JSONException e1) {
			Log.e(TAG, "Error parsing server response: " + responseStr);
		}
		
		//Log.i(TAG, "REST Event response: " + responseStr);
		
		List<EventItem> parsedEventItems = new ArrayList<EventItem>();
		JSONArray disruptions = null;
		if (response == null)
			return null;
		try {
			disruptions = response.getJSONArray("disruptions");
		} catch (JSONException e) {
			Log.e(TAG, "Error parsing disruptions array: " + responseStr);
		}
		
		
		for (int i = 0; i < disruptions.length(); i++ ){
			EventItem event = new EventItem();
			
			try {
				JSONObject JsonEvent = disruptions.getJSONObject(i);
				
				event.setEventID(JsonEvent.getString(EVENT_ID));
				
				event.setEventStartTime(
						stringToDate( 
								JsonEvent.getString(EVENT_START_DATE),
								JsonEvent.getString(EVENT_START_TIME) ));
						
				event.setEventEndTime(
						stringToDate( 
								JsonEvent.getString(EVENT_END_DATE),
								JsonEvent.getString(EVENT_END_TIME) ));
				
				event.setEventType(JsonEvent.getInt(EVENT_TYPE));
				event.setCategory(JsonEvent.getString(CATEGORY));
				event.setSector(JsonEvent.getString(SECTOR));		
				event.setLastModifiedTime(
						stringToDate( JsonEvent.getString(LAST_MODIFIED_TIME) ));
				
				event.setSeverity(JsonEvent.getString(SEVERITY));
				event.setPostCodeStart(JsonEvent.getString(POST_CODE_START));
				event.setPostCodeEnd(JsonEvent.getString(POST_CODE_END));
						
				event.setRemarkTime(
						stringToDate( 
								JsonEvent.getString(REMARK_DATE), 
								JsonEvent.getString(REMARK_TIME) ));
				
				event.setRemark(JsonEvent.getString(REMARK));
				
				event.setTitle(JsonEvent.getString(TITLE));
				event.setLocation(JsonEvent.getString(LOCATION));
				event.setDescription(JsonEvent.getString(DESCRIPTION));
				
				event.setLatitude(JsonEvent.getDouble(LATITUDE));
				event.setLongitude(JsonEvent.getDouble(LONGITUDE));
				
				//Distance to event
				if (locationManager == null && context != null)
					locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE); 
				Location lastKnownLocation = null;
				
				if (locationManager != null)
					lastKnownLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
			    
				if (lastKnownLocation != null){
					Log.i(TAG, "Current lat: " + lastKnownLocation.getLatitude() + ", long: " + lastKnownLocation.getLongitude());
			    Log.i(TAG, "Event lat: " + event.getLatitude() + ", long: " + event.getLongitude());
			    
			    float[] results = new float[3];
			    Location.distanceBetween(
			    		lastKnownLocation.getLatitude(), 
			    		lastKnownLocation.getLongitude(), 
			    		event.getLatitude(),
			    		event.getLongitude(),
			    		results);

			    	Log.i(TAG, "Distance to event: " + results[0] / 1000);
			    	event.setCurrentDistanceFromEvent(results[0] / 1000);
				}
			    
				
				parsedEventItems.add(event);
				
			} catch (JSONException e) {
				Log.e(TAG, "Error parsing disruption event: " + responseStr);
			}
				
		}
		
		return parsedEventItems;	
	}
	
	/*
	 * Date converter for JSON strings
	 * return Date
	 */
	private Date stringToDate(String date){
		//Date Format YYYY-MM-DD
		//may occasionally have time then the format is
		//YYYY-MM-DDTHHMM
		int year, month, day, hour, minute;
		
		if (date == null || date.equals(""))
			return null;
		
		try {
			year = Integer.parseInt( date.substring(0, 3) );
			month = Integer.parseInt( date.substring(5, 6) );
			day = Integer.parseInt( date.substring(8, 9) );
			
			if (date.length() == 15 ){
				hour = Integer.parseInt( date.substring(11, 12) );
				minute = Integer.parseInt( date.substring(13, 14));
				return new Date(year, month, day, hour, minute);
			}
			
			return new Date(year, month, day);
			
		} catch (NumberFormatException e){
			Log.e(TAG, "Error parsing date string: " + date);
		}
		
		return null;
	}
	
	private Date stringToDate(String date, String time){
		
		if ( date.equals("NULL") && time.equals("NULL"))
			return null;
		
		else if (time.equals("NULL"))
			return stringToDate(date);
		
		else if (date.equals("NULL"))
			return stringToDate("0000-00-00T" + time);
		
		return stringToDate(date + "T" + time);
	}
	
	public static List<TweetItem> parseTweets(String tweets){
		
		if ( tweets == null )
			return null;
		
		Log.i(TAG, "Response: " + tweets);
		
		JSONObject response = null;
		try {
			response = new JSONObject( tweets );
		} catch (JSONException e1) {
			Log.e(TAG, "Error parsing server response: " + tweets);
		}

		JSONArray disruptions = null;
		
		if (response == null)
			return null;
		try {
			disruptions = response.getJSONArray("tweets");
		} catch (JSONException e) {
			Log.e(TAG, "Error parsing disruptions array: " + tweets);
		}
		
		List<TweetItem> tweetList = new ArrayList<TweetItem>();
		
		Log.i(TAG, "REST Tweets response: " + tweets);
		
		
		for (int i = 0; i < disruptions.length(); i++ ){
			TweetItem tweet = new TweetItem();
			
			try {
				JSONObject JsonTweet = disruptions.getJSONObject(i);
				
				tweet.setTweetID(JsonTweet.getString(TWEET_ID));
				tweet.setAccountName(JsonTweet.getString(USER_NAME));
				tweet.setCreatedAt(JsonTweet.getString(CREATED_AT));
				tweet.setAccountLocation(JsonTweet.getString(ACCOUNT_LOCATION));
				tweet.setMessageText(JsonTweet.getString(MESSAGE_TEXT));
				tweet.setLatitude(JsonTweet.getDouble(TWEET_LATITUDE));
				tweet.setLongitude(JsonTweet.getDouble(TWEET_LONGITUDE));
				
				tweetList.add(tweet);
				
			} catch (JSONException e) {
				Log.e(TAG, "Error parsing tweets: " + tweets);
			}
				
		}
		
		return tweetList;
	}

}
