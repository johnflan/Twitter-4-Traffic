package uk.ac.ic.doc.t4t;

import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.LocationMgr;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import winterwell.jtwitter.OAuthSignpostClient;
import winterwell.jtwitter.Twitter;
import winterwell.jtwitter.TwitterException;
import oauth.signpost.*;
import oauth.signpost.commonshttp.CommonsHttpOAuthConsumer;
import oauth.signpost.commonshttp.CommonsHttpOAuthProvider;
import oauth.signpost.exception.OAuthCommunicationException;
import oauth.signpost.exception.OAuthExpectationFailedException;
import oauth.signpost.exception.OAuthMessageSignerException;
import oauth.signpost.exception.OAuthNotAuthorizedException;
import oauth.signpost.http.HttpParameters;
import oauth.signpost.http.HttpRequest;
import oauth.signpost.signature.OAuthMessageSigner;
import oauth.signpost.signature.SigningStrategy;
import android.app.Activity;
import android.content.Intent;
import android.location.Address;
import android.location.Geocoder;
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
	private OAuthConsumer mConsumer;
	private OAuthProvider mProvider;
	private OAuthSignpostClient oauthClient;
	
	private static final String CONSUMER_KEY = "5ZE33feiaV82U6WpkBdP6Q";
	private static final String CONSUMER_SECRET = "C60uB1YTai8HRHlKLSDfK16UcvmEcwGGFDcw3GYiWBM";
	
	private static final String OAUTH_KEY = "467904369-ojK1Gr0oW4Ydnb8fvn5XpXHC34O0fiPGDDO2XFUN";
	private static final String OAUTH_SECRET = "HM7GLfdZkW6eOQsXB73H8l2tdwCyLToGBXAhpoIrEw";
	
	//Response token: HkXiaEFt0Qgbby5VPOLvojpB3nOYgnOph1APat0
	//Response verifier: 5vHvfKZsKBneJ0AYmd5Y3DohtMcAw8bfIP0JIYKIAv4

	
	private static final String CALLBACK_URL = "right-turn://twitter";
	
	private static final String APP_HASH_TAG = "#RightTurn";
	
	private LocationMgr locationMgr;
	private List<Address> addresses;

	
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
        
        Geocoder geocoder = new Geocoder(this, Locale.getDefault());
        try {
			addresses = geocoder.getFromLocation(locationMgr.getLatitude(), locationMgr.getLongitude(), 1);
		} catch (IOException e) {
			e.printStackTrace();
		}
        
        mConsumer = new CommonsHttpOAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET);
        mProvider = new CommonsHttpOAuthProvider(
                "http://twitter.com/oauth/request_token",
                "http://twitter.com/oauth/access_token",
                "http://twitter.com/oauth/authorize");
        
        Log.d(TAG, "Location address " + addresses);
        
        trafficBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic jam");
				postTweet("Heavy traffic");
				
			}
		});
        
        roadworksBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting roadworks");
				postTweet("Road works");
				
			}
		});
        
        lightsOOOBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic lights our of order");
				postTweet("Traffic lights out of order");
				
			}
		});
        
        accidentBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic accident");
				postTweet("Traffic accident");
				
			}
		});
        
        weatherBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting dangerous driving conditions");
				postTweet("Dangerious driving conditions");
				
			}
		});
        
        roadClosedBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {			
				Log.i(TAG, "Reporting road closed");
				postTweet("Road closed");
			}
		});
        
    }
    
    private void postTweet(String msg){
    	
    	
    	Log.d(TAG, "Auth token: " + PreferencesHelper.getTwitterOAuthToken(this));
    	Log.d(TAG, "Auth verifier: " + PreferencesHelper.getTwitterOAuthVerifier(this));
    	
    	if (PreferencesHelper.getTwitterUsername(this).equals("")){
    		Log.i(TAG, "No twitter username configured");
    		Toast.makeText(ReportQuickEventActivity.this, "Error twitter not configured, you must enter your twitter username in the configuration screen.",Toast.LENGTH_LONG).show();
    		
    		//remove any existing oauth tokens
    		PreferencesHelper.setTwitterOAuthToken(this, "");
	    	PreferencesHelper.setTwitterOAuthVerifier(this, "");
	    	
	    	return;
    	}
    	
    	if (PreferencesHelper.getTwitterOAuthToken(this).equals("") || PreferencesHelper.getTwitterOAuthVerifier(this).equals("") ){
    		Log.i(TAG, "Requesting twitter oauth credentials");
    		String authUrl = null;
			try {
				
				Log.d(TAG, "mConsumer: " + mConsumer);
		        Log.d(TAG, "mProvider: " + mProvider);

				authUrl = mProvider.retrieveRequestToken(mConsumer, CALLBACK_URL);
				PreferencesHelper.setTwitterTempToken(this, mConsumer.getToken());
				PreferencesHelper.setTwitterTempTokenSecret(this, mConsumer.getTokenSecret());
			} catch (OAuthMessageSignerException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (OAuthNotAuthorizedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (OAuthExpectationFailedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (OAuthCommunicationException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
    		//oauthClient = new OAuthSignpostClient(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL);
    		
        	try {
        		//URI url = oauthClient.authorizeUrl();
        		//startActivity( new Intent(Intent.ACTION_VIEW, Uri.parse(url.toString())) );
        		startActivity( new Intent(Intent.ACTION_VIEW, Uri.parse(authUrl)) );
        	} catch (TwitterException e){
        		e.printStackTrace();
        	}
        	
    	} else {
    		
    		Log.i(TAG, "logging in for " + PreferencesHelper.getTwitterUsername(this));
    		Log.d(TAG, " with Response token: " + PreferencesHelper.getTwitterOAuthToken(this));
            Log.d(TAG, " and Response verifier: " + PreferencesHelper.getTwitterOAuthVerifier(this));
    		
    		oauthClient = new OAuthSignpostClient(
    				CONSUMER_KEY,
    				CONSUMER_SECRET,
    				PreferencesHelper.getTwitterOAuthToken(this),
    				PreferencesHelper.getTwitterOAuthVerifier(this) );

    		twitter = new Twitter(null, oauthClient);
    		
        	try
        	{
    	    	//Status to post in Twitter
        		
        		double location[] = {locationMgr.getLatitude(), locationMgr.getLongitude()};
        		twitter.setMyLocation(location);
        		
        		String tweet;
        		
        		if (addresses.size() > 0)
        			tweet = msg + " near " + addresses.get(0).getAddressLine(0) + ", " + addresses.get(0).getAddressLine(1);
        		else
        			tweet = msg;
        		
        		Log.i(TAG, "Tweet: " + tweet);
        		
        		if (tweet.length() > 129)
        			tweet = tweet.substring(0, 130);

    	    	twitter.setStatus(tweet + " " + APP_HASH_TAG);
    	    	
    	    	Toast.makeText(ReportQuickEventActivity.this, "Posted to Twitter", Toast.LENGTH_LONG).show();
        	}
        	catch(TwitterException.E401 e)
        	{
    	    	// comes here when username or password is wrongs
    	    	Toast.makeText(ReportQuickEventActivity.this, "Wrong Username or Password",Toast.LENGTH_LONG).show();
    	    	//PreferencesHelper.setTwitterOAuthToken(this, "");
    	    	//PreferencesHelper.setTwitterOAuthVerifier(this, "");
    	    	e.printStackTrace();
        	}
        	catch(Exception e)
        	{
        		Log.e(TAG, "Twitter exception: " + e.getMessage());
        		e.printStackTrace();
        		Toast.makeText(ReportQuickEventActivity.this, "Error posting to twitter",Toast.LENGTH_LONG).show();
        		
        	}
    		
    	}
    	
    	//ONCE THE MESSAGE HAS BEEN POSTED SHOULD FINISH THIS ACTIVITY

    }

	@Override
	protected void onResume() {
		super.onResume();
		
		mConsumer = new CommonsHttpOAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET);
		
		String mConsumerToken = PreferencesHelper.getTwitterTempToken(this);
		String mConsumerTokenSecret = PreferencesHelper.getTwitterTempTokenSecret(this);
		if (mConsumerToken != null && mConsumerTokenSecret != null){
			Log.i(TAG, "mConsumerToken " + mConsumerToken);
			Log.i(TAG, "mConsumerTokenSecret " + mConsumerTokenSecret);
			mConsumer.setTokenWithSecret(mConsumerToken, mConsumerTokenSecret);
		}
		
		Uri uri = this.getIntent().getData();
		//if (uri != null && uri.getScheme().equals(CALLBACK_URL)) {
	    if (uri != null ) {
	      Log.d(TAG, "callback: " + uri.getPath());

	      String verifier = uri.getQueryParameter(OAuth.OAUTH_VERIFIER);
	      Log.d(TAG, "verifier: " + verifier);


	      try {
	        // Get the token
	        Log.d(TAG, "mConsumer: " + mConsumer);
	        Log.d(TAG, "mProvider: " + mProvider);
	        mProvider.retrieveAccessToken(mConsumer, verifier);
	        String token = mConsumer.getToken();
	        String tokenSecret = mConsumer.getTokenSecret();
	        mConsumer.setTokenWithSecret(token, tokenSecret);

	        Log.d(TAG, String.format("verifier: %s, token: %s, tokenSecret: %s",
	            verifier, token, tokenSecret));

	        // Store token in prefs
	        //prefs.edit().putString("token", token).putString("tokenSecret",
	        //    tokenSecret).commit();
	        
	        PreferencesHelper.setTwitterOAuthToken(this, token);
	        PreferencesHelper.setTwitterOAuthVerifier(this, tokenSecret);

	        // Make a Twitter object
	        oauthClient = new OAuthSignpostClient(OAUTH_KEY, OAUTH_SECRET, token,
	            tokenSecret);
	        twitter = new Twitter("MarkoGargenta", oauthClient);

	        Log.d(TAG, "token: " + token);
	      } catch (oauth.signpost.exception.OAuthMessageSignerException e) {

	        e.printStackTrace();
	      } catch (oauth.signpost.exception.OAuthNotAuthorizedException e) {

	        e.printStackTrace();
	      } catch (oauth.signpost.exception.OAuthExpectationFailedException e) {

	        e.printStackTrace();
	      } catch (oauth.signpost.exception.OAuthCommunicationException e) {

	        e.printStackTrace();
	      }
	    }
		
//        if (uri != null) {
//        	Log.i(TAG, "Response data: " + uri);
//        	 String token = uri.getQueryParameter("oauth_token");
//             String verifier = uri.getQueryParameter("oauth_verifier");
//             
//             PreferencesHelper.setTwitterOAuthToken(this, token);
//             PreferencesHelper.setTwitterOAuthVerifier(this, verifier);
//             Log.d(TAG, "Response token: " + token);
//             Log.d(TAG, "Response verifier: " + verifier);
//        }

       
	}
    
}
