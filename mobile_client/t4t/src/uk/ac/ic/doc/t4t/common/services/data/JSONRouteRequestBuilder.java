package uk.ac.ic.doc.t4t.common.services.data;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

import uk.ac.ic.doc.t4t.ReportQuickEventActivity;
import uk.ac.ic.doc.t4t.eventmap.route.Route;
import uk.ac.ic.doc.t4t.eventmap.route.RoutePoint;

//{"points":[{"lon":"-0.18","lat":"51.51"},{"lon":"-0.10","lat":"51.47"}]}'

public class JSONRouteRequestBuilder {
	
	private static final String TAG = JSONRouteRequestBuilder.class.getSimpleName();
	
	private static final String POINTS_ARRAY = "points";
	private static final String LATITUDE = "lat";
	private static final String LONGITUDE = "lon";
	
	public static String parse(Route route){
		
		JSONObject routeJSON = new JSONObject();
		JSONArray pointArrayJSON = new JSONArray();

		
		for (RoutePoint point : route.getPoints()){
			JSONObject pointJSON = new JSONObject();
			
			try {
				
				if (point.getLatitude() == 0 && point.getLongitude() == 0)
					continue;
				
				pointJSON.put(LATITUDE, point.getLatitude());
				pointJSON.put(LONGITUDE, point.getLongitude());
				pointArrayJSON.put(pointJSON);
			} catch (JSONException e) {
				Log.e(TAG, "Error building route " + e.getMessage());
			}
		}
		
		try {
			routeJSON.put(POINTS_ARRAY, pointArrayJSON);
		} catch (JSONException e) {
			Log.e(TAG, "Error building route " + e.getMessage());
		}
		
		return routeJSON.toString();
	}

}
