package uk.ac.ic.doc.t4t.eventmap;

import uk.ac.ic.doc.t4t.eventlist.EventItem;

import com.google.android.maps.GeoPoint;
import com.google.android.maps.OverlayItem;

public class EventOverlayItem extends OverlayItem {
	
	private EventItem eventItem;

	public EventOverlayItem(GeoPoint point, String title, String snippet, EventItem eventItem) {
		super(point, title, snippet);
		// TODO Auto-generated constructor stub
		this.eventItem = eventItem.clone();
	}
	
	public EventItem getEventItem(){
		return eventItem;
	}

}
