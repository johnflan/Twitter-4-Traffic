package uk.ac.ic.doc.t4t;


import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Observable;
import java.util.Observer;


import com.markupartist.android.widget.PullToRefreshListView;
import com.markupartist.android.widget.PullToRefreshListView.OnRefreshListener;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.DataMgr;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventlist.EventItemAdapter;
import uk.ac.ic.doc.t4t.eventmap.route.Route;


import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.location.Address;
import android.location.Geocoder;
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
import android.widget.Toast;

public class EventListActivity extends Activity implements Observer {
	private final static String TAG = "EventListActivity";
	private PullToRefreshListView eventList;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	private LocationMgr location;
	private DataMgr restClient;
	private ImageButton reportEventBtn;
	private ImageView headerLogo;
	private boolean routeHomeLastState;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.eventlist);

        location = new LocationMgr(this);
        
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
				if (PreferencesHelper.getDisplayRouteHome(context)  &&
						( !PreferencesHelper.getRouteHomeHomeAddr(context).equals("") ||
		    			!PreferencesHelper.getRouteHomeWorkAddr(context).equals("")) ){
						
		        	new FetchRoute(context).execute(null);
					
					Log.i(TAG, "Loading route events");
		        	
		        } else {
		        	Log.i(TAG, "Loading all events");
		        	new FetchEvents(context).execute(null);
		        }
			}
		});
        
        eventList.setAdapter(new EventItemAdapter(this, R.layout.eventitem, eventItems));
        eventList.setClickable(true);
        
        routeHomeLastState = PreferencesHelper.getDisplayRouteHome(this);
        
        if (PreferencesHelper.getDisplayRouteHome(this)) {
    
		    if ( PreferencesHelper.getRouteHomeHomeAddr(this).equals("") ||
					PreferencesHelper.getRouteHomeWorkAddr(this).equals("")){
					
					Toast.makeText(this, "You must set your home and work locations to view a route", 
			                Toast.LENGTH_LONG).show();
					new FetchEvents(this).execute(null);
					
				} else {
					
		        	new FetchRoute(this).execute(null);
				}
			
			new FetchRoute(this).execute(null);
            
        } else if (!PreferencesHelper.getDisplayRouteHome(this)){
        	new FetchEvents(this).execute(null);
        }
        
    }
    
    @Override
	protected void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		
		Log.d(TAG, "(onResume) Display only route: " + PreferencesHelper.getDisplayRouteHome(this));
		
		if (routeHomeLastState != PreferencesHelper.getDisplayRouteHome(this)){
			if (PreferencesHelper.getDisplayRouteHome(this) &&
	        		!PreferencesHelper.getRouteHomeHomeAddr(this).equals("") &&
	    			!PreferencesHelper.getRouteHomeWorkAddr(this).equals("")){
				
				new FetchRoute(this).execute(null);
	            
	        } else if (!PreferencesHelper.getDisplayRouteHome(this)){
	        	new FetchEvents(this).execute(null);
	        }
			routeHomeLastState = PreferencesHelper.getDisplayRouteHome(this);
		}

		
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
			eventItems.clear();
			
			if (events != null)
				eventItems.addAll(events);
			
	        eventList.onRefreshComplete();
	    }
	}
	
	private class FetchRouteEvents extends AsyncTask<Route, Void, List<EventItem>>{

		private Context context;
		private DataMgr restClient;
		
		public FetchRouteEvents(Context context){
			this.context = context;
			restClient = new DataMgr(context);
		}

		
		@Override
		protected List<EventItem> doInBackground(Route... params) {
			
			return restClient.requestRouteEvents(params[0]);
		}
		
		@Override
	    protected void onPostExecute(List<EventItem> events) {
			Log.i(TAG, "Populating list view");
			eventItems.clear();
			
			if (events != null)
				eventItems.addAll(events);
			
	        eventList.onRefreshComplete();
	    }
	}
	
	private class FetchRoute extends AsyncTask<Void, Void, Route>{

		private Context context;
		private DataMgr restClient;
		
		//London bounding box
		private static final double LDN_LOWER_LEFT_LATITUDE = 51.25;
		private static final double LDN_LOWER_LEFT_LONGITUDE = -0.598;
		private static final double LDN_UPPER_RIGHT_LATITUDE = 51.75;
		private static final double LDN_UPPER_RIGHT_LONGITUDE = 0.372;
		private static final int MAX_RESULTS = 1;
		
		public FetchRoute(Context context){
			this.context = context;
			restClient = new DataMgr(context);
		}

		
		@Override
		protected Route doInBackground(Void... params) {
			
			Log.i(TAG, "Requesting route");
			
			Log.d(TAG, "Home addr: " + PreferencesHelper.getRouteHomeHomeAddr(context));
			Log.d(TAG, "Work addr: " + PreferencesHelper.getRouteHomeWorkAddr(context));
			
			if (!PreferencesHelper.getRouteHomeHomeAddr(context).equals("") &&
        			!PreferencesHelper.getRouteHomeWorkAddr(context).equals("")){
				
				Geocoder geocoder = new Geocoder(context, Locale.getDefault());
				List<Address> homeAddresses;
				List<Address> workAddresses;
				Route route = null;
				
		        try {
					homeAddresses = geocoder.getFromLocationName(
							PreferencesHelper.getRouteHomeHomeAddr(context),
							MAX_RESULTS,
							LDN_LOWER_LEFT_LATITUDE, 
							LDN_LOWER_LEFT_LONGITUDE, 
							LDN_UPPER_RIGHT_LATITUDE, 
							LDN_UPPER_RIGHT_LONGITUDE);
					
					
					workAddresses = geocoder.getFromLocationName(
							PreferencesHelper.getRouteHomeWorkAddr(context),
							MAX_RESULTS,
							LDN_LOWER_LEFT_LATITUDE, 
							LDN_LOWER_LEFT_LONGITUDE, 
							LDN_UPPER_RIGHT_LATITUDE, 
							LDN_UPPER_RIGHT_LONGITUDE);
					
					
					route = restClient.getRoute(
							homeAddresses.get(0).getLatitude(),
							homeAddresses.get(0).getLongitude(), 
							workAddresses.get(0).getLatitude(), 
							workAddresses.get(0).getLongitude());
					
					restClient.requestRouteEvents(route);
					
				} catch (IOException e) {
					Log.e(TAG, e.getMessage());
				}
				
				return route;
			}
			
			return null;
		}
		
		@Override
	    protected void onPostExecute(Route route) {
			
			if (route != null){
				new FetchRouteEvents(context).execute(route);
			}
				
	    }
	}

}
