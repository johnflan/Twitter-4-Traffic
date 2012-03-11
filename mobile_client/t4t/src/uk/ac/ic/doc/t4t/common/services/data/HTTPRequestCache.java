package uk.ac.ic.doc.t4t.common.services.data;

import java.util.List;

import android.content.ContentValues;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.Cursor;
import android.util.Log;


import uk.ac.ic.doc.t4t.eventlist.EventItem;

public class HTTPRequestCache {
	
	private final static String TAG = HTTPRequestCache.class.getSimpleName();
	
	private static final String DB_NAME = "right_turn.db";
	private static final String EVENT_CACHE_TABLE = "eventcache";
	private final Context context;
	private SQLiteDatabase database;
	
	public HTTPRequestCache(Context context){
		this.context = context;
	}
	
	
	private void createOrOpenDatabase() {
		Log.i(TAG, "Opening or creating cache database");
		database = context.openOrCreateDatabase(DB_NAME, context.MODE_PRIVATE, null);
		database.execSQL("CREATE TABLE IF NOT EXISTS "
			     + EVENT_CACHE_TABLE
			     + " (eventlist TEXT);");	
	}


	public String getEventItems(){
		Log.v(TAG, "Requesting cached events");
		
		createOrOpenDatabase();

		String response = null;
		
		try {
			Cursor cursor = database.rawQuery("SELECT * FROM " + EVENT_CACHE_TABLE , null);
			int eventListCol = cursor.getColumnIndex("eventlist");
			
			Log.i(TAG, "Loading request cache from DB with " + cursor.getCount() + " row(s)");
			
			// Check if our result was valid.
			if (cursor.getCount() > 0){
				cursor.moveToFirst();
				if (cursor != null) {		
					do {
						response = cursor.getString(eventListCol);
					} while(cursor.moveToNext());
				}	
			}
		
		} catch(Exception e) {
			Log.e(TAG, "Error", e);
		} finally {
			if (database != null)
				database.close();
		}
		
		return response;
	}
	
	public void setEventItems(String eventItemsResponse){
		Log.v(TAG, "Storing events in cache");
		
		createOrOpenDatabase();
		
		try {
			//remove existing response
			database.delete(EVENT_CACHE_TABLE, null, null);
			
			ContentValues eventlist = new ContentValues();                          
			eventlist.put("eventlist", eventItemsResponse);
			
			database.insert(EVENT_CACHE_TABLE, null, eventlist);

		} catch(Exception e) {
			Log.e(TAG, "Error", e);
		} finally {
			if (database != null)
				database.close();
		}
		
	}

}
