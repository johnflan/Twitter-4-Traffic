package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;
import java.util.Observable;
import java.util.Observer;

import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.DataMgr;
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
import android.location.Location;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageButton;

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
        
        //Here we set the rest client as a listener for the location service
        //so once a location is returned, we can make a HTTP request.       
        restClient = new DataMgr(this);
        restClient.addObserver(this);
        
        
        location = new LocationMgr(this);
        location.addLocationObserver(restClient); 
       
        mapController = mapView.getController();
        mapView.setBuiltInZoomControls(true);  
        mapController.setZoom(15);

        
        Drawable drawable = this.getResources().getDrawable(R.drawable.map_pointer);
        eventOverlay = new EventOverlay(drawable, this);
        
        findMyLocation(location);

        Route route = restClient.getRoute(51.46670983333333, -0.12208916666666665, 51.52263, -0.071926);
        RouteOverlay mapOverlay = new RouteOverlay(route, mapView);
        mapOverlays.add(mapOverlay);
        
        new FetchEvents(this).execute(null);
        
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
			if (events != null)
				addEventOverlay(events);
	    }
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
	

}
