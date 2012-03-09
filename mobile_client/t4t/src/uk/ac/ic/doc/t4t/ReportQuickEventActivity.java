package uk.ac.ic.doc.t4t;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import uk.ac.ic.doc.t4t.common.services.LocationMgr;
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
import android.app.Activity;
import android.app.Dialog;
import android.content.DialogInterface;
import android.content.DialogInterface.OnCancelListener;
import android.content.Intent;
import android.location.Address;
import android.location.Geocoder;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

public class ReportQuickEventActivity extends Activity {
	private static final String TAG = ReportQuickEventActivity.class.getSimpleName();
	
	private ImageButton btnTraffic;
	private ImageButton btnRoadworks;
	private ImageButton btnLightsOOO;
	private ImageButton btnAccident;
	private ImageButton btnHazard;
	private ImageButton btnRoadClosed;
	
	private Twitter twitter;
	private OAuthConsumer mConsumer;
	private OAuthProvider mProvider;
	private OAuthSignpostClient oauthClient;
	
	private LocationMgr locationMgr;
	private List<Address> addresses;
	
	private static final String CONSUMER_KEY = "5ZE33feiaV82U6WpkBdP6Q";
	private static final String CONSUMER_SECRET = "C60uB1YTai8HRHlKLSDfK16UcvmEcwGGFDcw3GYiWBM";	
	private static final String OAUTH_KEY = "467904369-ojK1Gr0oW4Ydnb8fvn5XpXHC34O0fiPGDDO2XFUN";
	private static final String OAUTH_SECRET = "HM7GLfdZkW6eOQsXB73H8l2tdwCyLToGBXAhpoIrEw";
	private static final String CALLBACK_URL = "right-turn://twitter";
	
	private static final String APP_HASH_TAG = "#RightTurn";
	
	private static final String REPORT_TEXT_TRAFFIC_CONGESTION = "Traffic congestion";
	private static final String REPORT_TEXT_ROAD_WORKS = "Road works";
	private static final String REPORT_TEXT_TRAFFIC_LIGHTS = "Traffic lights out of order";
	private static final String REPORT_TEXT_TRAFFIC_ACCIDENT = "Traffic accident";
	private static final String REPORT_TEXT_HAZARD = "Hazard";
	private static final String REPORT_TEXT_ROAD_CLOSED = "Road closed";
	
	private static final String REPORT_ADV_TEXT_DAMAGED_ROAD_SURFACE = "Damaged road surface";
	private static final String REPORT_ADV_TEXT_ICY_ROAD = "Ice on road";
	private static final String REPORT_ADV_TEXT_SLIPARY_SURFACE = "Slipary road surface";
	private static final String REPORT_ADV_TEXT_BURST_WATER_MAIN = "Burst water main";
	private static final String REPORT_ADV_TEXT_ROAD_OBSTRUCTION = "Dangerous object on road";
	
	private static final String REPORT_TEXT_MINOR = "minor";
	private static final String REPORT_TEXT_MODERATE = "moderate";
	private static final String REPORT_TEXT_SEVERE = "severe";
	
	private String eventTypeMsg;
	private Dialog dialog;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.reportevent);
        
        btnTraffic = 	(ImageButton) findViewById(R.id.reportTrafficJam);
        btnRoadworks = 	(ImageButton) findViewById(R.id.reportRoadworks);
        btnLightsOOO = 	(ImageButton) findViewById(R.id.reportOOOTrafficLights);
        btnAccident = 	(ImageButton) findViewById(R.id.reportTrafficAccident);
        btnHazard = 	(ImageButton) findViewById(R.id.reportHazard);
        btnRoadClosed = (ImageButton) findViewById(R.id.reportRoadClosed);
        
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
        
        btnTraffic.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic jam");
				reportEvent(REPORT_TEXT_TRAFFIC_CONGESTION);
			}
		});
        
        btnRoadworks.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting roadworks");
				reportEvent(REPORT_TEXT_ROAD_WORKS);
			}
		});
        
        btnLightsOOO.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic lights our of order");
				reportEvent(REPORT_TEXT_TRAFFIC_LIGHTS);
			}
		});
        
        btnAccident.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting traffic accident");
				reportEvent(REPORT_TEXT_TRAFFIC_ACCIDENT);
			}
		});
        
        btnHazard.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Reporting driving hazard");
				reportComplexEvent(REPORT_TEXT_HAZARD);
			}
		});
        
        btnRoadClosed.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {			
				Log.i(TAG, "Reporting road closed");
				reportEvent(REPORT_TEXT_ROAD_CLOSED);
			}
		});
        
    }
    
    private void reportEvent(String msg){
    	
    	this.eventTypeMsg = msg;
    	if (verifiedTwitterAccount()) {
    		
    		dialog = new Dialog(ReportQuickEventActivity.this);
    		dialog.requestWindowFeature(dialog.getWindow().FEATURE_NO_TITLE);
            dialog.setContentView(R.layout.report_question_popup);

            dialog.setCancelable(true);
            
            //wire up the selection options
            Button minorBtn = (Button) dialog.findViewById(R.id.reportMinorEvent);
            Button moderateBtn = (Button) dialog.findViewById(R.id.reportModerateEvent);
            Button seriousBtn = (Button) dialog.findViewById(R.id.reportSevereEvent);

            TextView eventDescription = (TextView) dialog.findViewById(R.id.reportEventType);
            eventDescription.setText( "Reporting " + eventTypeMsg + "\nPlease rate the severity");
            
            minorBtn.setOnClickListener(new OnClickListener() {
            @Override
                public void onClick(View v) {
            		sendTweet(REPORT_TEXT_MINOR);
                    finish();
                }
            });
            
            moderateBtn.setOnClickListener(new OnClickListener() {
                @Override
                    public void onClick(View v) {
                		sendTweet(REPORT_TEXT_MODERATE);
                        finish();
                    }
            });
            
            seriousBtn.setOnClickListener(new OnClickListener() {
                @Override
                    public void onClick(View v) {
                		sendTweet(REPORT_TEXT_SEVERE);
                        finish();
                    }
            });
            
            dialog.setOnCancelListener(new OnCancelListener() {
				
				@Override
				public void onCancel(DialogInterface dialog) {
					eventTypeMsg = null;
					
				}
			});
            
            dialog.show();

    	}
    }
    
    public void reportComplexEvent(String msg){
    	this.eventTypeMsg = msg;
    	
    	if (verifiedTwitterAccount()) {
    		
    		dialog = new Dialog(ReportQuickEventActivity.this);
    		dialog.requestWindowFeature(dialog.getWindow().FEATURE_NO_TITLE);
            dialog.setContentView(R.layout.report_question_advanced_popup);

            dialog.setCancelable(true);
            //there are a lot of settings, for dialog, check them all out!
            
            TextView eventDescription = (TextView) dialog.findViewById(R.id.reportEventType);
            eventDescription.setText( "Reporting hazardous conditions");
    		
            //map buttons
            Button btnDangerousRoadSurface = (Button) dialog.findViewById(R.id.reportAdvDangerousRoadSurface);
            Button btnIcyRoad = (Button) dialog.findViewById(R.id.reportAdvIcyConditions);
            Button btnSliparySurface = (Button) dialog.findViewById(R.id.reportAdvSliparySurface);
            Button btnBurstWaterMain = (Button) dialog.findViewById(R.id.reportAdvBurstWaterMain);
            Button btnRoadObstruction = (Button) dialog.findViewById(R.id.reportAdvRoadObstruction);
            
            btnDangerousRoadSurface.setOnClickListener(new View.OnClickListener() {
				
				@Override
				public void onClick(View v) {
					sendTweet(REPORT_ADV_TEXT_DAMAGED_ROAD_SURFACE);
					finish();
				}
			});
            
            btnIcyRoad.setOnClickListener(new View.OnClickListener() {
				
				@Override
				public void onClick(View v) {
					sendTweet(REPORT_ADV_TEXT_ICY_ROAD);
					finish();
				}
			});
            
            btnSliparySurface.setOnClickListener(new View.OnClickListener() {
				
				@Override
				public void onClick(View v) {
					sendTweet(REPORT_ADV_TEXT_SLIPARY_SURFACE);
					finish();
				}
			});
            
            btnBurstWaterMain.setOnClickListener(new View.OnClickListener() {
				
				@Override
				public void onClick(View v) {
					sendTweet(REPORT_ADV_TEXT_BURST_WATER_MAIN);
					finish();
				}
			});
            
            btnRoadObstruction.setOnClickListener(new View.OnClickListener() {
				
				@Override
				public void onClick(View v) {
					sendTweet(REPORT_ADV_TEXT_ROAD_OBSTRUCTION);
					finish();
				}
			});
            
            dialog.setOnCancelListener(new OnCancelListener() {
				
				@Override
				public void onCancel(DialogInterface dialog) {
						eventTypeMsg = null;
					
				}
			});
            
            dialog.show();
    	}
    	
    }

	@Override
	protected void onPause() {
		// TODO Auto-generated method stub
		super.onPause();
		
		if(dialog != null){
			try{
				dialog.dismiss();
			} catch (Exception e){
				e.printStackTrace();
			}
			
		}
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
	    if (uri != null ) {
	      Log.d(TAG, "callback: " + uri.getPath());

	      String verifier = uri.getQueryParameter(OAuth.OAUTH_VERIFIER);
	      Log.d(TAG, "verifier: " + verifier);

	      try {
	        // Get the token
	        mProvider.retrieveAccessToken(mConsumer, verifier);
	        String token = mConsumer.getToken();
	        String tokenSecret = mConsumer.getTokenSecret();
	        mConsumer.setTokenWithSecret(token, tokenSecret);
	        
	        PreferencesHelper.setTwitterOAuthToken(this, token);
	        PreferencesHelper.setTwitterOAuthVerifier(this, tokenSecret);

	        // Make a Twitter object
	        oauthClient = new OAuthSignpostClient(OAUTH_KEY, OAUTH_SECRET, token,
	            tokenSecret);
	        twitter = new Twitter("MarkoGargenta", oauthClient);

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
		       
	}
	
	public boolean verifiedTwitterAccount(){
		
		Log.d(TAG, "Auth token: " + PreferencesHelper.getTwitterOAuthToken(this));
    	Log.d(TAG, "Auth verifier: " + PreferencesHelper.getTwitterOAuthVerifier(this));
    	
    	if (PreferencesHelper.getTwitterUsername(this).equals("")){
    		Log.i(TAG, "No twitter username configured");
    		Toast.makeText(ReportQuickEventActivity.this,
    				"Error twitter not configured",Toast.LENGTH_LONG).show();
    		
    		//remove any existing oauth tokens
    		PreferencesHelper.setTwitterOAuthToken(this, "");
	    	PreferencesHelper.setTwitterOAuthVerifier(this, "");
	    	
	    	return false;
    	}
    	
    	if (PreferencesHelper.getTwitterOAuthToken(this).equals("") || 
    			PreferencesHelper.getTwitterOAuthVerifier(this).equals("") ){
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
    		
        	try {
        		startActivity( new Intent(Intent.ACTION_VIEW, Uri.parse(authUrl)) );
        	} catch (TwitterException e){
        		e.printStackTrace();
        	}
        	
        	return false;       	
    	} 
    	
    	return true;
		
	}
	
	
	public void sendTweet(String severity){
		
		// Normal tweet format:
		// (EVENT_TYPE) causing (SEVERITY) problems near (ADDRESS) #RightTurn
		// Hazard tweet format:
		// (HAZARD TYPE) near (ADDRESS) #RightTurn
		
		if (this.eventTypeMsg == null)
			return;
		
		String tweet;
		
		// different tweet format for hazards
		if (this.eventTypeMsg.equals(REPORT_TEXT_HAZARD))
			tweet = severity;
		else
			tweet = this.eventTypeMsg + " causing " + severity + " problems";
		
		if (addresses != null && addresses.size() > 0)
			tweet = tweet + " near " + addresses.get(0).getAddressLine(0) + ", " + addresses.get(0).getAddressLine(1);

		Log.i(TAG, "Tweet: " + tweet);
		
		// A much more comprehensive mechanism was suggested by Luke for shortening
		// the tweet if its too long, we could look for and replace the following
		// street with st
		// road with rd
		// London with Ldn
		
		if (tweet.length() > 129)
			tweet = tweet.substring(0, 130);

	    postTweet( tweet + " " + APP_HASH_TAG );
	    
	    this.eventTypeMsg = null;
	}
	
	private void postTweet(String message){
		try {
    		Log.i(TAG, "logging in for " + PreferencesHelper.getTwitterUsername(this));
    		Log.d(TAG, " with Response token: " + PreferencesHelper.getTwitterOAuthToken(this));
            Log.d(TAG, " and Response verifier: " + PreferencesHelper.getTwitterOAuthVerifier(this));
    		
    		oauthClient = new OAuthSignpostClient(
    				CONSUMER_KEY,
    				CONSUMER_SECRET,
    				PreferencesHelper.getTwitterOAuthToken(this),
    				PreferencesHelper.getTwitterOAuthVerifier(this) );

    		twitter = new Twitter(null, oauthClient);
    		
    		double location[] = {locationMgr.getLatitude(), locationMgr.getLongitude()};
    		
    		twitter.setMyLocation(location);
	    	twitter.setStatus( message );
	    	
	    	Toast.makeText(ReportQuickEventActivity.this, "Posted to Twitter", Toast.LENGTH_LONG).show();
    	}
    	catch(TwitterException.E401 e)
    	{
	    	// comes here when username or password is wrongs
	    	Toast.makeText(ReportQuickEventActivity.this, "Wrong Username or Password",Toast.LENGTH_LONG).show();
	    	PreferencesHelper.setTwitterOAuthToken(this, "");
	    	PreferencesHelper.setTwitterOAuthVerifier(this, "");
	    	e.printStackTrace();
    	}
    	catch(Exception e)
    	{
    		Log.e(TAG, "Twitter exception: " + e.getMessage());
    		e.printStackTrace();
    		Toast.makeText(ReportQuickEventActivity.this, "Error posting to twitter",Toast.LENGTH_LONG).show();
    	}
	}
}
