package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;


import android.app.Activity;
import android.os.Bundle;
import android.widget.ListView;

public class EventListActivity extends Activity {
	
	private ListView eventList;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.eventlist);
        
        eventItems.add(new EventItem());
        eventItems.add(new EventItem());
        eventItems.add(new EventItem());
        eventItems.add(new EventItem());
        eventItems.add(new EventItem());
        eventItems.add(new EventItem());
        
        eventList = (ListView)findViewById(R.id.eventList);
        
        eventList.setAdapter(new EventItemAdapter(this, R.layout.eventitem, eventItems));
        eventList.setClickable(true);
    }

}
