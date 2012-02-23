package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;
import java.util.Observable;
import java.util.Observer;

import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.common.services.RESTClient;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventmap.EventOverlay;

import com.google.android.maps.GeoPoint;
import com.google.android.maps.MapActivity;
import com.google.android.maps.MapController;
import com.google.android.maps.MapView;
import com.google.android.maps.Overlay;
import com.google.android.maps.OverlayItem;

import android.app.Activity;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageButton;

public class EventMapActivity extends MapActivity implements Observer {
	private final static String TAG = "EventMapActivity";
	private ImageButton reportEventBtn;
	private LocationMgr location;
	private RESTClient restClient;
	private List<EventItem> eventItems = new ArrayList<EventItem>();
	private MapView mapView;
	private List<Overlay> mapOverlays;
	private EventOverlay eventOverlay;

	@Override
	protected boolean isRouteDisplayed() {
		// TODO Auto-generated method stub
		return false;
	}

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.eventmap);
        
        reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventMapActivity.this, ReportEventActivity.class);
				startActivity(i);	
			}
		});
        
        
        mapView = (MapView) findViewById(R.id.mapview);
        mapOverlays = mapView.getOverlays();
        Drawable drawable = this.getResources().getDrawable(R.drawable.map_pointer);
        eventOverlay = new EventOverlay(drawable, this);
        
        //Here we set the rest client as a listener for the location service
        //so once a location is returned, we can make a HTTP request.       
        restClient = new RESTClient(this);
        restClient.addObserver(this);
        
        location = new LocationMgr(this);
        location.addLocationObserver(restClient); 
       
        MapController mapController = mapView.getController();
        mapController.animateTo(location.getGeoPoint());
        mapController.setZoom(6);
        
    }


	@Override
	public void update(Observable observable, Object data) {
		if (!observable.equals(restClient))
			return;
		
		Log.i(TAG, "Updating event list");
		eventItems = (List<EventItem>) data;
		
		addEventOverlay(eventItems);
		
	}
	
	private void addEventOverlay(List<EventItem> eventItems) {
		
		for (EventItem event : eventItems){

			GeoPoint point = new GeoPoint(
					(int) (event.getLatitude() * 1E6),
					(int) (event.getLongitude() * 1E6) );
			OverlayItem overlayitem = new OverlayItem(
												point,
												event.getTitle(),
												event.getDescription());
			
			eventOverlay.addOverlay(overlayitem);
		}
		
        
        mapOverlays.add(eventOverlay);
		
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
        
            case R.id.menu_show_map:
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
	

}
