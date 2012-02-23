package uk.ac.ic.doc.t4t.common;

import uk.ac.ic.doc.t4t.R;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;

public class PreferencesHelper {
	public final static String PREFS_NAME = "t4t_prefs";
	
	private final static String DEFAULT_SERVER_URL = "http://vm-project-g1153006.doc.ic.ac.uk";
	private final static String DEFAULT_SERVER_PORT = "55003";
	private final static String DEFAULT_VIEW = "map";
	
    public static String getServerURL(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        return prefs.getString(
        		context.getString(R.string.pref_server_url_key),
        		DEFAULT_SERVER_URL);
        
    }
 
    public static void setServerURL(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_server_url_key),
                newValue);
        prefsEditor.commit();
    }
    
    public static String getServerPort(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_server_port_key),
        		DEFAULT_SERVER_PORT);
        
    }
 
    public static void setServerPort(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_server_port_key),
                newValue);
        prefsEditor.commit();
    }
    
    public static String getDefaultView(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_default_view_key),
        		DEFAULT_VIEW);
        
    }
 
    public static void setDefaultView(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_default_view_key),
                newValue);
        prefsEditor.commit();
    }
}
