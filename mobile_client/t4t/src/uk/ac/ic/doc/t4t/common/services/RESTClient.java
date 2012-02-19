package uk.ac.ic.doc.t4t.common.services;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.List;
import java.util.Observable;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.conn.HttpHostConnectException;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventlist.EventItem;

import android.content.Context;
import android.location.Location;
import android.location.LocationManager;
import android.text.format.Time;
import android.util.Log;

public class RESTClient extends Observable implements LocationObserver {
	
	private final static String TAG = "RESTClient";
	private Context context;
	private HttpClient httpclient;
	private HttpGet request;
	private boolean hasLocation = false;
	private String URL = "http://vm-project-g1153006.doc.ic.ac.uk:55003";
	private double latitude;
	private double longitude;
	
	private String apiVersion = "/t4t/0.1/";
	private String disruptionsEndpoint = "disruptions?";	
	private String tweetsEndpoint = "tweets?disruptionID=";
	
	private JSONParser jsonParser;
	
	List<EventItem> eventItems = new ArrayList<EventItem>();
	
	public RESTClient(Context context){
		  this.context = context;
	}
	
	public void requestEvents(){
		
		httpclient = new DefaultHttpClient();

		String query = apiVersion + disruptionsEndpoint + "latitude=" + latitude + "&longitude=" + longitude + "&radius=10";
		request = new HttpGet(URL + query);
		
		Log.i(TAG, "Requesting: " + URL + query);
		
		String response = null;
		ResponseHandler<String> handler = new BasicResponseHandler();  
        try {  
			response = httpclient.execute(request, handler);

        } catch (HttpHostConnectException e) {
        	Log.e(TAG, "Error contacting server: " + e.getMessage());
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        
        if (jsonParser == null)
        	jsonParser = new JSONParser(context);
        
        eventItems = jsonParser.parseDisruptionEvents(response);
        httpclient.getConnectionManager().shutdown();
        
        Log.i(TAG, "Notifying observers of new event list");
		setChanged();
		notifyObservers(eventItems);
	}

	@Override
	public void notifyLocationUpdate(double latitude, double longitude) {
		
		Log.i(TAG, "notifyLocationUpdate");
		
		this.latitude = latitude;
		this.longitude = longitude;
		
		requestEvents();
		
	}
	
	public List<TweetItem> requestTweets(String eventID){
		httpclient = new DefaultHttpClient();

		String query = apiVersion + tweetsEndpoint + eventID;
		request = new HttpGet(URL + query);
		
		Log.i(TAG, "Requesting: " + URL + query);
		
		String response = null;
		ResponseHandler<String> handler = new BasicResponseHandler();  
        try {  
			response = httpclient.execute(request, handler);

        } catch (HttpHostConnectException e) {
        	Log.e(TAG, "Error contacting server: " + e.getMessage());
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        
        if (jsonParser == null)
        	jsonParser = new JSONParser(context);

        httpclient.getConnectionManager().shutdown();
        
		return jsonParser.parseTweets(response);
	}
}


