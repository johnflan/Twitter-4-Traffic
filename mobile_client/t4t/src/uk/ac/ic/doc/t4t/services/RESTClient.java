package uk.ac.ic.doc.t4t.services;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Observable;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import uk.ac.ic.doc.t4t.EventItem;

import android.content.Context;
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
	
	List<EventItem> eventItems = new ArrayList<EventItem>();
	
	public RESTClient(Context context){
		  
	}
	
	public void requestEvents(){
		
		httpclient = new DefaultHttpClient();

		String query = apiVersion + disruptionsEndpoint + "latitude=" + latitude + "&longitude=" + longitude + "&radius=10";
		request = new HttpGet(URL + query);
		
		Log.i(TAG, "Requesting: " + URL + query);
		
		JSONObject response = null;
		ResponseHandler<String> handler = new BasicResponseHandler();  
        try {  
            try {
				response = new JSONObject( httpclient.execute(request, handler) );
			} catch (JSONException e) {
				Log.e(TAG, "Error parsing data "+e.toString());
			}  
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        parseJsonEvents(response);
        httpclient.getConnectionManager().shutdown();
        
		
	}

	private void parseJsonEvents(JSONObject response) {
		
		Log.i(TAG, "REST Event response: " + response.toString());
		
		List<EventItem> parsedEventItems = new ArrayList<EventItem>();
		JSONArray disruptions = null;
		if (response == null)
			return;
		try {
			disruptions = response.getJSONArray("disruptions");
		} catch (JSONException e) {
			Log.e(TAG, "Error parsing disruptions array: " + response.toString());
		}
		
		
		for (int i = 0; i < disruptions.length(); i++ ){
			EventItem event = new EventItem();
			
			try {
				JSONObject JsonEvent = disruptions.getJSONObject(i);
				
				event.setEventID(JsonEvent.getString(EVENT_ID));
				
				event.setTitle(JsonEvent.getString(TITLE));
				event.setLocation(JsonEvent.getString(LOCATION));
				event.setDescription(JsonEvent.getString(DESCRIPTION));
				
				parsedEventItems.add(event);
				
			} catch (JSONException e) {
				Log.e(TAG, "Error parsing disruption event: " + response.toString());
			}
				
		}
		
		eventItems = parsedEventItems;
		Log.i(TAG, "Notifying observers of new event list");
		setChanged();
		notifyObservers(parsedEventItems);
		
	}

	@Override
	public void notifyLocationUpdate(double latitude, double longitude) {
		
		Log.i(TAG, "notifyLocationUpdate");
		
		this.latitude = latitude;
		this.longitude = longitude;
		
		requestEvents();
		
	}}


