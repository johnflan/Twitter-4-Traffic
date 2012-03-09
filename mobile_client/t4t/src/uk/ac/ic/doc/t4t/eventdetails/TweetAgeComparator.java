package uk.ac.ic.doc.t4t.eventdetails;

import java.util.Comparator;


public class TweetAgeComparator implements Comparator<TweetItem>{

	@Override
	public int compare(TweetItem object1, TweetItem object2) {
		
		if( object1.getAgeMillis() > object2.getAgeMillis() )
			return -1;
		
		else if( object1.getAgeMillis() < object2.getAgeMillis() )
			return 1;
		
		else
			return 0;
	}

}
