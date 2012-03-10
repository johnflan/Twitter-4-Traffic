package uk.ac.ic.doc.t4t.common;

import uk.ac.ic.doc.t4t.R;
import winterwell.jtwitter.Twitter.IHttpClient;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;

public class PreferencesHelper {
	public final static String PREFS_NAME = "t4t_prefs";
	
	private final static String DEFAULT_SERVER_URL = "http://vm-project-g1153006.doc.ic.ac.uk";
	private final static String DEFAULT_SERVER_PORT = "55004";
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

	public static String getTwitterUsername(Context context) {
		SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_twitter_username_key),
        		DEFAULT_VIEW);
	}

	
    public static String getTwitterOAuthToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_twitter_oauth_key),
        		"");
        
    }
 
    public static void setTwitterOAuthToken(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_twitter_oauth_key),
                newValue);
        prefsEditor.commit();
    }
    
    public static String getTwitterOAuthVerifier(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_twitter_oauth_token),
        		"");
        
    }
 
    public static void setTwitterOAuthVerifier(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_twitter_oauth_token),
                newValue);
        prefsEditor.commit();
    }
    
    
    public static String getTwitterTempToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		"twitter_temp_token",
        		"");
        
    }
 
    public static void setTwitterTempToken(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                "twitter_temp_token",
                newValue);
        prefsEditor.commit();
    }
    
    public static String getTwitterTempTokenSecret(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		"twitter_temp_token_secret",
        		"");
        
    }
 
    public static void setTwitterTempTokenSecret(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                "twitter_temp_token_secret",
                newValue);
        prefsEditor.commit();
    }
    
    public static String getServerRequestRadius(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_server_radius_key),
        		"3000");
        
    }
 
    public static void setServerRequestRadius(Context context, String newValue) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Editor prefsEditor = prefs.edit();
        prefsEditor.putString(
                context.getString(R.string.pref_server_radius_key),
                newValue);
        prefsEditor.commit();
    }
    
    public static String getTweetSortType(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getString(
        		context.getString(R.string.pref_sort_tweets_key),
        		"age");
        
    }
    
    public static boolean getProfanityFilter(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        
        return prefs.getBoolean(
        		context.getString(R.string.pref_profanity_filter_key),
        		false);
        
    }

	
	
}
