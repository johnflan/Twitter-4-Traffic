package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;

import uk.ac.ic.doc.t4t.common.services.LocationObserver;
import uk.ac.ic.doc.t4t.service.RetrieveTrafficEvents;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;

public class UpdaterService extends Service implements LocationListener {
	private static final String TAG = UpdaterService.class.getSimpleName();
	
	private static final long MINIMUM_DISTANCE_CHANGE_FOR_UPDATES = 1; 
	private static final long MINIMUM_TIME_BETWEEN_UPDATES = 1000; 	
	protected LocationManager locationManager;
	private List<LocationObserver> locationObservers = new ArrayList<LocationObserver>();
	
	private RetrieveTrafficEvents eventRetriever;

	@Override
	public void onCreate() {
		super.onCreate();
		
		eventRetriever = new RetrieveTrafficEvents();
		
		requestLocation();
	}

	private void requestLocation() {
		
		locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE); 

        locationManager.requestLocationUpdates(
        		LocationManager.NETWORK_PROVIDER, 
        		MINIMUM_TIME_BETWEEN_UPDATES, 
        		MINIMUM_DISTANCE_CHANGE_FOR_UPDATES,
        		this
        );
        
        //Get the last known location to speedup the process
        Location lastKnownLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        onLocationChanged(lastKnownLocation);
        
	}

	@Override
	public synchronized void onDestroy() {
		super.onDestroy();
		
		if (eventRetriever.isRunning()){
			eventRetriever.interrupt();
		}
		
		eventRetriever = null;
	}

	@Override
	public synchronized void onStart(Intent intent, int startId) {
		super.onStart(intent, startId);
		
		if (!eventRetriever.isRunning()){
			eventRetriever.start();
		}
		
	}

	//used for IPC
	@Override
	public IBinder onBind(Intent arg0) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void onLocationChanged(Location location) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onProviderDisabled(String provider) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onProviderEnabled(String provider) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onStatusChanged(String provider, int status, Bundle extras) {
		// TODO Auto-generated method stub
		
	}
	

}
