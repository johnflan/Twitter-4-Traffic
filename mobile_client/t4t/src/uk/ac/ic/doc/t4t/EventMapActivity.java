package uk.ac.ic.doc.t4t;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Observable;
import java.util.Observer;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.DataMgr;
import uk.ac.ic.doc.t4t.common.services.location.LocationObserver;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventmap.EventOverlay;
import uk.ac.ic.doc.t4t.eventmap.EventOverlayItem;
import uk.ac.ic.doc.t4t.eventmap.route.Route;
import uk.ac.ic.doc.t4t.eventmap.route.RouteOverlay;
import uk.ac.ic.doc.t4t.eventmap.route.RoutePoint;

import com.google.android.maps.GeoPoint;
import com.google.android.maps.MapActivity;
import com.google.android.maps.MapController;
import com.google.android.maps.MapView;
import com.google.android.maps.MyLocationOverlay;
import com.google.android.maps.Overlay;
import com.google.android.maps.OverlayItem;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.graphics.drawable.Drawable;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorListener;
import android.hardware.SensorManager;
import android.location.Address;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Debug;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageButton;
import android.widget.Toast;

public class EventMapActivity extends MapActivity implements Observer {
	private static final String TAG = EventMapActivity.class.getSimpleName();
	private ImageButton reportEventBtn;
	private LocationMgr location;
	private DataMgr restClient;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	private MapView mapView;
	private List<Overlay> mapOverlays;
	private EventOverlay eventOverlay;
	private MapController mapController;
	private MyLocationOverlay myLocationOverlay;
	private boolean displayingRouteHome = false;
	private RouteOverlay mapRouteOverlay;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.eventmap);
        
        reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventMapActivity.this, ReportQuickEventActivity.class);
				startActivity(i);	
			}
		});
        
        mapView = (MapView) findViewById(R.id.mapview);

        mapOverlays = mapView.getOverlays();
        
        location = new LocationMgr(this);

        mapController = mapView.getController();
        mapView.setBuiltInZoomControls(true);  
        mapController.setZoom(14);
        
        Drawable drawable = this.getResources().getDrawable(R.drawable.map_pointer);
        eventOverlay = new EventOverlay(drawable, this);
        
        findMyLocation(location);
        
    }
    


	@Override
	protected void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		
		if (myLocationOverlay != null)
			myLocationOverlay.enableMyLocation();
		
		Log.d(TAG, "(onResume) Display only route: " + PreferencesHelper.getDisplayRouteHome(this));
		
		if (PreferencesHelper.getDisplayRouteHome(this)){
			

			if (PreferencesHelper.getRouteHomeHomeAddr(this).equals("") ||
    			PreferencesHelper.getRouteHomeWorkAddr(this).equals("")){
				
				Toast.makeText(this, "You must set your home and work locations to view a route", 
		                Toast.LENGTH_LONG).show();
				new FetchEvents(this).execute(null);
			} else {
				new FetchRoute(this).execute(null);
			}

            
        } else if (!PreferencesHelper.getDisplayRouteHome(this) && displayingRouteHome){
        	new FetchEvents(this).execute(null);
        	displayingRouteHome = false;
        	mapOverlays.remove(mapRouteOverlay);
        } else {
        	Log.d(TAG, "(onResume) Requesting all events");
        	new FetchEvents(this).execute(null);
        }

	}
	
    @Override
	protected void onPause() {
		// TODO Auto-generated method stub
		super.onPause();
		
		if (myLocationOverlay != null)
			myLocationOverlay.disableMyLocation();
	}

	private void findMyLocation(LocationMgr location){
        myLocationOverlay = new MyLocationOverlay(this, mapView);
        myLocationOverlay.enableMyLocation();
        
        mapController.animateTo(location.getGeoPoint());
        mapController.setCenter(location.getGeoPoint());
        mapView.getOverlays().add(myLocationOverlay);
        mapView.postInvalidate();
    }

	
	private void addEventOverlay(List<EventItem> eventItems) {
		Log.i(TAG, "Adding new overlay");
		
		eventOverlay.clearOverlays();
		
		for (EventItem event : eventItems){

			GeoPoint point = new GeoPoint(
					(int) (event.getLatitude() * 1E6),
					(int) (event.getLongitude() * 1E6) );
			EventOverlayItem overlayitem = new EventOverlayItem(
												point,
												event.getTitle(),
												event.getDescription(),
												event);
			
			eventOverlay.addOverlay(overlayitem);
			
		}
		
        
        mapOverlays.add(eventOverlay);
        
		//forces a redraw of the map to show the overlay
        mapView.invalidate();
	}


	@Override  
    public boolean onCreateOptionsMenu(Menu menu) {
		MenuInflater inflater = getMenuInflater();
		inflater.inflate(R.menu.event_map_options_menu, menu);
		return true;
    }
	
	@Override
    public boolean onOptionsItemSelected(MenuItem item) {
		Intent i;
        switch (item.getItemId()) {
        
            case R.id.menu_show_list:
            	i = new Intent(EventMapActivity.this, EventListActivity.class);
                startActivity(i);
                break;
                
            case R.id.menu_about:
            	i = new Intent(EventMapActivity.this, AboutApplicationActivity.class);
                startActivity(i);
                break;
                
            case R.id.menu_settings:
            	i = new Intent(EventMapActivity.this, PreferenceActivity.class);
                startActivity(i);
                break;
        }
        return true;
    }
	
	@Override
	public void update(Observable observable, Object data) {
		if (!observable.equals(restClient))
			return;
		
		Log.i(TAG, "Updating event list");
		addEventOverlay( (List<EventItem>) data );
		
	}

	@Override
	protected boolean isRouteDisplayed() {
		// TODO Auto-generated method stub
		return false;
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
			
			if (events != null){
				Log.d(TAG, "Got " + events.size() + " events");
				addEventOverlay(events);
			}
				
			
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
			
			if (events != null){
				Log.d(TAG, "Got " + events.size() + " events");
				addEventOverlay(events);
			}
				
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
				mapRouteOverlay = new RouteOverlay(route, mapView);
				mapOverlays.add(mapRouteOverlay);
				displayingRouteHome = true;
				new FetchRouteEvents(context).execute(route);
			}
				
	    }
	}


}
