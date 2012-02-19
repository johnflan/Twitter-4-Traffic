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
	
	private LocationManager locationManager;
	
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
        parseJsonEvents(response);
        httpclient.getConnectionManager().shutdown();
        
		
	}

	private void parseJsonEvents(String responseStr) {
		
		if ( responseStr == null )
			return;
		
		Log.i(TAG, "Response: " + responseStr);
		
		JSONObject response = null;
		try {
			response = new JSONObject( responseStr );
		} catch (JSONException e1) {
			Log.e(TAG, "Error parsing server response: " + responseStr);
		}
		
		Log.i(TAG, "REST Event response: " + responseStr);
		
		List<EventItem> parsedEventItems = new ArrayList<EventItem>();
		JSONArray disruptions = null;
		if (response == null)
			return;
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
		
		eventItems = parsedEventItems;
		Log.i(TAG, "Notifying observers of new event list");
		setChanged();
		notifyObservers(parsedEventItems);
		
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

	@Override
	public void notifyLocationUpdate(double latitude, double longitude) {
		
		Log.i(TAG, "notifyLocationUpdate");
		
		this.latitude = latitude;
		this.longitude = longitude;
		
		requestEvents();
		
	}}


