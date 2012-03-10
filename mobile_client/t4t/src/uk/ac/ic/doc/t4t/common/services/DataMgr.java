package uk.ac.ic.doc.t4t.common.services;

import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;
import java.util.Observable;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.SAXException;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.data.EventPostProcessor;
import uk.ac.ic.doc.t4t.common.services.data.GoogleKMLHandler;
import uk.ac.ic.doc.t4t.common.services.data.HTTPRequestCache;
import uk.ac.ic.doc.t4t.common.services.data.HTTPRequester;
import uk.ac.ic.doc.t4t.common.services.data.JSONParser;
import uk.ac.ic.doc.t4t.common.services.data.TweetPostProcessor;
import uk.ac.ic.doc.t4t.common.services.location.LocationObserver;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventmap.route.Route;

import uk.ac.ic.doc.t4t.common.services.data.RoadProvider;

import android.content.Context;
import android.util.Log;

public class DataMgr extends Observable implements LocationObserver {
	
	private static final String TAG = DataMgr.class.getSimpleName();
	private Context context;
	private boolean hasLocation = false;
	
	private double latitude;
	private double longitude;
	
	private String apiVersion = "/t4t/0.2/";
	private static final String DISRUPTIONS_ENDPOINT = "disruptions?";	
	private static final String TWEETS_ENDPOINT = "tweets?disruptionID=";
	private static final String PROFANITY_FILTER_TRUE = "&filter=y";
	private static final String PROFANITY_FILTER_FALSE = "&filter=n";
	private final String profanityParameter;
	private final String eventRadius;
	private final String URL;
	
	private HTTPRequestCache requestCache;
	private EventPostProcessor eventPostProcessor;
	private TweetPostProcessor tweetPostProcessor;
	
	List<EventItem> eventItems = new ArrayList<EventItem>();
	
	public DataMgr(Context context){
		  this.context = context;
		  eventRadius = PreferencesHelper.getServerRequestRadius(context);
		  URL = PreferencesHelper.getServerURL(context) + ":" + 
				  PreferencesHelper.getServerPort(context);
		  
		  boolean profanityFilter = PreferencesHelper.getProfanityFilter(context);
		  
		  if (profanityFilter)
			  profanityParameter = PROFANITY_FILTER_TRUE;
		  else
			  profanityParameter = PROFANITY_FILTER_FALSE;
		  
		  
		  requestCache = new HTTPRequestCache(this.context);
		  eventPostProcessor = new EventPostProcessor(this.context);
		  tweetPostProcessor = new TweetPostProcessor(this.context);
	}
	
	public List<EventItem> requestEvents(){
		
		String response;
		
		if (hasLocation == false){
			
			response = requestCache.getEventItems();
		    
		    eventItems = JSONParser.parseDisruptionEvents(response);
			
		} else {
			
			String query = apiVersion + DISRUPTIONS_ENDPOINT + "latitude=" +
					latitude + "&longitude=" + longitude + "&radius=" + eventRadius;

			response = HTTPRequester.httpGet(URL + query);
			
			if (response == null){
				Log.i(TAG, "Received no response ");
				return null;
			}
			Log.i(TAG, "Response length " + response.length());
			
			requestCache.setEventItems(response);

		    eventItems = JSONParser.parseDisruptionEvents(response);
		    
		}
		
		if (eventItems != null){
			
			eventItems = eventPostProcessor.processEvents(eventItems);
			Log.i(TAG, "Parsed " + eventItems.size() + " event items");
	        
		}
		return eventItems;
		
	}

	@Override
	public void notifyLocationUpdate(double latitude, double longitude) {
		
		Log.i(TAG, "Got new location");
		this.hasLocation = true;
		this.latitude = latitude;
		this.longitude = longitude;
		
		requestEventsForObservers();
	}
	
	private void requestEventsForObservers() {
		List<EventItem> newEvents;
		newEvents = requestEvents();
		
		notifyObservers(newEvents);
		
	}

	public List<TweetItem> requestTweets(String eventID){

		String query = apiVersion + TWEETS_ENDPOINT + eventID + profanityParameter;       
        String response = HTTPRequester.httpGet(URL + query);
        
        List<TweetItem> tweets = JSONParser.parseTweets(response);
        
        if (tweets != null){
			
			tweets = tweetPostProcessor.processTweets(tweets);
			Log.i(TAG, "Parsed " + tweets.size() + " tweets");
	        
		}
        
		return tweets;
	}
	
	public Route getRoute(double fromLat, double fromLon, double toLat, double toLon){
		
		StringBuffer urlString = new StringBuffer();
		urlString.append("http://maps.google.com/maps?f=d&hl=en");
		urlString.append("&saddr=");// from
		urlString.append(Double.toString(fromLat));
		urlString.append(",");
		urlString.append(Double.toString(fromLon));
		urlString.append("&daddr=");// to
		urlString.append(Double.toString(toLat));
		urlString.append(",");
		urlString.append(Double.toString(toLon));
		urlString.append("&ie=UTF8&0&om=0&output=kml");
		  
		
		//String response = HTTPRequester.httpGet( urlString.toString() );
		InputStream is = null;
		URLConnection conn;
		try {
			conn = new java.net.URL(urlString.toString()).openConnection();
			is = conn.getInputStream();
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		Log.i(TAG, "Route response: " + is);
		
		RoadProvider provider = new RoadProvider();
		
		Route route = provider.getRoute(is);
		
		Log.i(TAG, "Route response: " + route);
		
        return route;

	}

}




