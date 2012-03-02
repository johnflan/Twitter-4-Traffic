package uk.ac.ic.doc.t4t.common.services;

import java.util.ArrayList;
import java.util.List;
import java.util.Observable;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.data.EventPostProcessor;
import uk.ac.ic.doc.t4t.common.services.data.HTTPRequestCache;
import uk.ac.ic.doc.t4t.common.services.data.HTTPRequester;
import uk.ac.ic.doc.t4t.common.services.data.JSONParser;
import uk.ac.ic.doc.t4t.common.services.location.LocationObserver;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventlist.EventItem;

import android.content.Context;
import android.util.Log;

public class DataMgr extends Observable implements LocationObserver {
	
	private static final String TAG = DataMgr.class.getSimpleName();
	private Context context;
	private boolean hasLocation = false;
	
	private double latitude;
	private double longitude;
	
	private String apiVersion = "/t4t/0.1/";
	private static final String DISRUPTIONS_ENDPOINT = "disruptions?";	
	private static final String TWEETS_ENDPOINT = "tweets?disruptionID=";
	private final String URL;
	
	private JSONParser jsonParser;
	private HTTPRequestCache requestCache;
	private EventPostProcessor eventPostProcessor;
	
	List<EventItem> eventItems = new ArrayList<EventItem>();
	
	public DataMgr(Context context){
		  this.context = context;
		  URL = PreferencesHelper.getServerURL(context) + ":" + 
				  PreferencesHelper.getServerPort(context);
		  
		  requestCache = new HTTPRequestCache(this.context);
		  eventPostProcessor = new EventPostProcessor(this.context);
	}
	
	public void requestEvents(){
		
		String response;
		
		if (hasLocation == false){
			
			response = requestCache.getEventItems();
			
			if (jsonParser == null)
		    	jsonParser = new JSONParser(context);
		    
		    eventItems = jsonParser.parseDisruptionEvents(response);
			
		} else {
			
			String query = apiVersion + DISRUPTIONS_ENDPOINT + "latitude=" +
					latitude + "&longitude=" + longitude + "&radius=10";

			response = HTTPRequester.httpGet(URL + query);
			
			requestCache.setEventItems(response);
		    
		    if (jsonParser == null)
		    	jsonParser = new JSONParser(context);
		    
		    eventItems = jsonParser.parseDisruptionEvents(response);
		    
		}
		
		
        
        Log.i(TAG, "Notifying observers of new event list");
		setChanged();
		notifyObservers(eventItems);
	}

	@Override
	public void notifyLocationUpdate(double latitude, double longitude) {
		
		Log.i(TAG, "notifyLocationUpdate");
		this.hasLocation = true;
		this.latitude = latitude;
		this.longitude = longitude;
		
		requestEvents();	
	}
	
	public List<TweetItem> requestTweets(String eventID){

		String query = apiVersion + TWEETS_ENDPOINT + eventID;       
        String response = HTTPRequester.httpGet(URL + query);
        
		return JSONParser.parseTweets(response);
	}
}


