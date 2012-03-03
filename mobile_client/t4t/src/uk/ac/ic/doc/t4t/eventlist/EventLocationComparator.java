package uk.ac.ic.doc.t4t.eventlist;

import java.util.Comparator;


public class EventLocationComparator implements Comparator<EventItem> {

	
	// The compare method compares its two arguments, returning a negative integer,
	// 0, or a positive integer depending on whether the first argument is less than,
	// equal to, or greater than the second.
	//		if(empAge1>empAge2) return 1;
	//		else if(empAge1<empAge2) return -1;
	//		else return 0;
	
	@Override
	public int compare(EventItem object1, EventItem object2) {
				
		double object1Distance = object1.getCurrentDistanceFromEvent();
		double object2Distance = object2.getCurrentDistanceFromEvent();
		
		if(object1Distance>object2Distance)
			return 1;
		
		else if(object1Distance<object2Distance)
			return -1;
		
		else
			return 0;

	}

}
