package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;
import java.util.Observable;
import java.util.Observer;

import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.RESTClient;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventlist.EventItemAdapter;


import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;

public class EventListActivity extends Activity implements Observer {
	private final static String TAG = "EventListActivity";
	private ListView eventList;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	private LocationMgr location;
	private RESTClient restClient;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.eventlist);
        
        //Here we set the rest client as a listener for the location service
        //so once a location is returned, we can make a HTTP request.       
        restClient = new RESTClient(this);
        restClient.addObserver(this);
        
        location = new LocationMgr(this);
        location.addLocationObserver(restClient); 
        
        eventList = (ListView)findViewById(R.id.eventList);
        
        //make the event clickable
        eventList.setOnItemClickListener( new AdapterView.OnItemClickListener() {
			public void onItemClick(AdapterView<?> adapterView, View view, int position, long id) {
				EventItem currentItem = (EventItem) adapterView.getItemAtPosition(position);
				
					Log.i(TAG, "Opening event: " + currentItem.getTitle());
					
					Intent i = new Intent(EventListActivity.this, EventDetailsActivity.class);
					i.putExtra("EventDetails", currentItem);
					startActivity(i);

			}
		});
    }

	@Override
	public void update(Observable observable, Object data) {
		
		if (!observable.equals(restClient))
			return;
		
		Log.i(TAG, "Updating event list");
		eventItems = (List<EventItem>) data;


        eventList.setAdapter(new EventItemAdapter(this, R.layout.eventitem, eventItems));
        eventList.setClickable(true);
        
       
		
	}

}
