package uk.ac.ic.doc.t4t;

import java.net.URI;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import winterwell.jtwitter.OAuthSignpostClient;
import winterwell.jtwitter.Twitter;
import winterwell.jtwitter.TwitterException;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Toast;

public class ReportQuickEventActivity extends Activity {
	private static final String TAG = UpdaterService.class.getSimpleName();
	private ImageButton trafficBtn;
	private ImageButton roadworksBtn;
	private ImageButton lightsOOOBtn;
	private ImageButton accidentBtn;
	private ImageButton weatherBtn;
	private ImageButton roadClosedBtn;
	
	private Twitter twitter;
	
	private static final String CONSUMER_KEY = "5ZE33feiaV82U6WpkBdP6Q";
	private static final String CONSUMER_SECRET = "C60uB1YTai8HRHlKLSDfK16UcvmEcwGGFDcw3GYiWBM";
	
	private static final String OAUTH_KEY = "467904369-ojK1Gr0oW4Ydnb8fvn5XpXHC34O0fiPGDDO2XFUN";
	private static final String OAUTH_SECRET = "HM7GLfdZkW6eOQsXB73H8l2tdwCyLToGBXAhpoIrEw";
	
	private static final String CALLBACK_URL = "right-turn://twitter";
	
	private LocationMgr locationMgr;

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.reportevent);
        
        trafficBtn = 	(ImageButton) findViewById(R.id.reportTrafficJam);
        roadworksBtn = 	(ImageButton) findViewById(R.id.reportRoadworks);
        lightsOOOBtn = 	(ImageButton) findViewById(R.id.reportOOOTrafficLights);
        accidentBtn = 	(ImageButton) findViewById(R.id.reportTrafficAccident);
        weatherBtn = 	(ImageButton) findViewById(R.id.reportWeather);
        roadClosedBtn = (ImageButton) findViewById(R.id.reportRoadClosed);
        
        locationMgr = new LocationMgr(this);
        
        trafficBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic jam");
				
			}
		});
        
        roadworksBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting roadworks");
				
			}
		});
        
        lightsOOOBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic lights our of order");
				
			}
		});
        
        accidentBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic accident");
				
			}
		});
        
        weatherBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting dangerous driving conditions");
				
			}
		});
        
        roadClosedBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting road closed");
				postTweet("Road closed at  #RightTurn");
			}
		});
        
    }
    
    private void postTweet(String msg){
    	
    	Log.d(TAG, "Auth token: " + PreferencesHelper.getTwitterOAuthToken(this));
    	Log.d(TAG, "Auth verifier: " + PreferencesHelper.getTwitterOAuthVerifier(this));
    	
    	if (PreferencesHelper.getTwitterOAuthToken(this).equals("") || PreferencesHelper.getTwitterOAuthVerifier(this).equals("") ){
    		Log.i(TAG, "Requesting twitter oauth credentials");
    		
    		OAuthSignpostClient oauthClient = new OAuthSignpostClient(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL);
        	URI url = oauthClient.authorizeUrl();        	
        	startActivity( new Intent(Intent.ACTION_VIEW, Uri.parse(url.toString())) );
    	} else {
    		
    		Log.i(TAG, "logging in for " + PreferencesHelper.getTwitterUsername(this));
    		// Make a Twitter object
    		
    		Log.d(TAG, "OAUTH_KEY: " + OAUTH_KEY);
    		Log.d(TAG, "OAUTH_SECRET: " + OAUTH_SECRET);
    		Log.d(TAG, "PreferencesHelper.getTwitterOAuthToken(this): " + PreferencesHelper.getTwitterOAuthToken(this));
    		Log.d(TAG, "PreferencesHelper.getTwitterOAuthVerifier(this): " + PreferencesHelper.getTwitterOAuthVerifier(this));
    		//OAuthSignpostClient client = new OAuthSignpostClient(
    		//		OAUTH_KEY,
    		//		OAUTH_SECRET,
    		//		PreferencesHelper.getTwitterOAuthToken(this),
    		//		PreferencesHelper.getTwitterOAuthVerifier(this) );
    		
    		OAuthSignpostClient client = new OAuthSignpostClient(
    				CONSUMER_KEY,
    				CONSUMER_SECRET,
    				OAUTH_KEY,
    				OAUTH_SECRET);

    		twitter = new Twitter("t4traffic", client);
    		
    	}

    	
    	try
    	{
	    	//Status to post in Twitter
    		
    		double location[] = {locationMgr.getLatitude(), locationMgr.getLongitude()};
    		twitter.setMyLocation(location);

	    	twitter.setStatus(msg);
	    	Toast.makeText(ReportQuickEventActivity.this, "Article Posted to Twitter Successfully!!", Toast.LENGTH_SHORT).show();
    	}
    	catch(TwitterException.E401 e)
    	{
	    	// comes here when username or password is wrongs
	    	Toast.makeText(ReportQuickEventActivity.this, "Wrong Username or Password, Kindly Check your logins",Toast.LENGTH_SHORT).show();
	    	//PreferencesHelper.setTwitterOAuthToken(this, "");
	    	//PreferencesHelper.setTwitterOAuthVerifier(this, "");
	    	e.printStackTrace();
    	}
    	catch(Exception e)
    	{
    		Log.e(TAG, "Twitter exception: " + e.getMessage());
    		e.printStackTrace();
    		Toast.makeText(ReportQuickEventActivity.this, "Network Host not responding",Toast.LENGTH_SHORT).show();
    		
    	}
    }

	@Override
	protected void onResume() {
		super.onResume();
		
		Uri uri = this.getIntent().getData();
        if (uri != null) {
        	 String token = uri.getQueryParameter("oauth_token");
             String verifier = uri.getQueryParameter("oauth_verifier");
             PreferencesHelper.setTwitterOAuthToken(this, token);
             PreferencesHelper.setTwitterOAuthVerifier(this, verifier);
             Log.d(TAG, "response token: " + token);
             Log.d(TAG, "Response verifier: " + verifier);
        }

       
	}
    
}
