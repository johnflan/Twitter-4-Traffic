package uk.ac.ic.doc.t4t;


import java.util.ArrayList;
import java.util.List;
import java.util.Observable;
import java.util.Observer;


import com.markupartist.android.widget.PullToRefreshListView;
import com.markupartist.android.widget.PullToRefreshListView.OnRefreshListener;

import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.DataMgr;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventlist.EventItemAdapter;


import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ImageButton;
import android.widget.ImageView;

public class EventListActivity extends Activity implements Observer {
	private final static String TAG = "EventListActivity";
	private PullToRefreshListView eventList;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	private LocationMgr location;
	private DataMgr restClient;
	private ImageButton reportEventBtn;
	private ImageView headerLogo;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.eventlist);
        
        //Here we set the rest client as a listener for the location service
        //so once a location is returned, we can make a HTTP request.       
        restClient = new DataMgr(this);
        restClient.addObserver(this);
        
        
        location = new LocationMgr(this);
        location.addLocationObserver(restClient); 
        
        eventList = (PullToRefreshListView)findViewById(R.id.eventList);
        
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
        
        reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {
			
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventListActivity.this, ReportQuickEventActivity.class);
				startActivity(i);
				
			}
		});
        
                
        eventList.setOnRefreshListener(new OnRefreshListener() {
			
			@Override
			public void onRefresh() {
				Context context = getApplicationContext();
				new FetchEvents(context).execute(null);
			}
		});
        
        eventList.setAdapter(new EventItemAdapter(this, R.layout.eventitem, eventItems));
        eventList.setClickable(true);
        
        new FetchEvents(this).execute(null);
        
    }

	@Override
	public void update(Observable observable, Object data) {
		
		if (!observable.equals(restClient))
			return;
		
		Log.i(TAG, "Updating event list");
		eventItems = (List<EventItem>) data;

	}
	
	private void populateEvents(List<EventItem> events){
		eventList.setAdapter(new EventItemAdapter(this, R.layout.eventitem, eventItems));
        eventList.setClickable(true);
	}
	
	@Override  
    public boolean onCreateOptionsMenu(Menu menu) {
		MenuInflater inflater = getMenuInflater();
		inflater.inflate(R.menu.event_list_options_menu, menu);
		return true;
    }
	
	@Override
    public boolean onOptionsItemSelected(MenuItem item) {
		Intent i;
        switch (item.getItemId()) {
        
            case R.id.menu_show_map:
            	i = new Intent(EventListActivity.this, EventMapActivity.class);
                startActivity(i);
                break;
                
            case R.id.menu_about:
            	i = new Intent(EventListActivity.this, AboutApplicationActivity.class);
                startActivity(i);
                break;
                
            case R.id.menu_settings:
            	i = new Intent(EventListActivity.this, PreferenceActivity.class);
                startActivity(i);
                break;
        }
        return true;
    }
	
	private class FetchEvents extends AsyncTask<Void, Void, List<EventItem>>{

		private Context context;
		private DataMgr restClient;
		
		public FetchEvents(Context context){
			this.context = context;
			restClient = new DataMgr(context);
		}

		
		@Override
		protected List<EventItem> doInBackground(Void... params) {
			return restClient.requestEvents();
		}
		
		@Override
	    protected void onPostExecute(List<EventItem> events) {
			Log.i(TAG, "Populating list view");
	        //populateEvents(events);
			eventItems.clear();
			
			if (events != null)
				eventItems.addAll(events);
			
	        eventList.onRefreshComplete();
	    }

		
	}

}
