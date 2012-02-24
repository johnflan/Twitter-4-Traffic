package uk.ac.ic.doc.t4t.common.services;

import java.util.ArrayList;
import java.util.List;

import uk.ac.ic.doc.t4t.UpdaterService;

import com.google.android.maps.GeoPoint;

import android.content.Context;
import android.location.LocationListener;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.location.Location;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;

public class LocationMgr implements LocationListener{
	private static final String TAG = UpdaterService.class.getSimpleName();
	private static final long MINIMUM_DISTANCE_CHANGE_FOR_UPDATES = 1; 
	private static final long MINIMUM_TIME_BETWEEN_UPDATES = 1000; 	
	protected LocationManager locationManager;
	private Context context;
	private List<LocationObserver> locationObservers = new ArrayList<LocationObserver>();
	
	private double latitude;
	private double longitude;
	
	public LocationMgr(Context context){
		
		this.context = context;
		
        locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE);       
        locationManager.requestLocationUpdates(
        		LocationManager.NETWORK_PROVIDER, 
        		MINIMUM_TIME_BETWEEN_UPDATES, 
        		MINIMUM_DISTANCE_CHANGE_FOR_UPDATES,
        		this
        );
        
        //Get the last known location to speedup the process
        Location lastKnownLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        onLocationChanged(lastKnownLocation);
        
        Log.i(TAG, "Location requested");
		
	}
	
	public double getLatitude(){
		return latitude;
	}
	
	public double getLongitude(){
		return longitude;
	}
	
	public GeoPoint getGeoPoint(){
		GeoPoint point = new GeoPoint(
				(int) (latitude * 1E6),
				(int) (longitude  * 1E6) );
		return point;
	}
	
	public void addLocationObserver(LocationObserver locationObserver){
		locationObservers.add(locationObserver);
	}

	@Override
	public void onLocationChanged(android.location.Location location) {
		if (location == null)
			return;
		
		latitude = location.getLatitude();
		longitude = location.getLongitude();
		
		for (LocationObserver locObserver : locationObservers)
			locObserver.notifyLocationUpdate(latitude, longitude);
		
		Log.i(TAG, "Got location, lat " + latitude + ", long " + longitude);
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
