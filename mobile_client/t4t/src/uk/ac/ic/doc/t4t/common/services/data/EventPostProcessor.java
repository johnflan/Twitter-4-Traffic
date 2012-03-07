package uk.ac.ic.doc.t4t.common.services.data;

import java.util.Collections;
import java.util.List;

import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventlist.EventLocationComparator;
import android.content.Context;
import android.location.Location;
import android.location.LocationManager;
import android.util.Log;

public class EventPostProcessor {
	private static final String TAG = EventPostProcessor.class.getSimpleName();
	private LocationManager locationManager;
	private Context context;
	
	
	public EventPostProcessor(Context context){
		this.context = context;
		locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE); 	
	}
	
	public List<EventItem> processEvents(List<EventItem> eventList){
		
		//Calculate the users distance from each event
		Location lastKnownLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
		calculateDistanceFromEvent(eventList, lastKnownLocation);
		
		
		//Sort events for list view, promote closer events to top of the list
		Collections.sort(eventList, new EventLocationComparator());
		
		return eventList;	
	}
	
	private List<EventItem> calculateDistanceFromEvent(List<EventItem> eventList, Location currentLocation){

		Log.i(TAG, "Calculating distance for each event to current location lat:"
				+ currentLocation.getLatitude()
				+ ", long:" + currentLocation.getLongitude());

		for (EventItem event : eventList){
			
		    float[] results = new float[3];
		    Location.distanceBetween(
		    		currentLocation.getLatitude(), 
		    		currentLocation.getLongitude(), 
		    		event.getLatitude(),
		    		event.getLongitude(),
		    		results);

	    	event.setCurrentDistanceFromEvent(results[0] / 1000);
		}
	    
		return eventList;
	}

}
