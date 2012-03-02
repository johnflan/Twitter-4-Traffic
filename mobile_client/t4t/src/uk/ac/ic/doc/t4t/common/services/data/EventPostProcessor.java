package uk.ac.ic.doc.t4t.common.services.data;

import java.util.List;

import uk.ac.ic.doc.t4t.eventlist.EventItem;
import android.content.Context;
import android.location.LocationManager;

public class EventPostProcessor {
	
	private LocationManager locationManager;
	private Context context;
	
	public EventPostProcessor(Context context){
		this.context = context;
	}
	
	public List<EventItem> processEvents(List<EventItem> eventList){
		
		calculateDistanceFromEvent(eventList);
		
		return eventList;	
	}
	
	private List<EventItem> calculateDistanceFromEvent(List<EventItem> eventList){
		
		return eventList;
	}

}
