package uk.ac.ic.doc.t4t;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;

public class SplashScreenActivity extends Activity {

	private final int SPLASH_DISPLAY_LENGTH = 1000;
	private String defaultView;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.splash);
        
        defaultView = PreferencesHelper.getDefaultView(this);
        
        //startService(new Intent(this, UpdaterService.class));
        //stopService(new Intent(this, UpdaterService.class));
    	
        new Handler().postDelayed(new Runnable(){
    		 
            @Override
            public void run() {

            	
                /* Create an Intent that will start the Menu-Activity. */
            	
            	Intent mainIntent;
            	
            	if (defaultView.equals("map"))
           		
            		mainIntent = new Intent(SplashScreenActivity.this, EventMapActivity.class);
            	else
            		mainIntent = new Intent(SplashScreenActivity.this, EventListActivity.class);
            	
            	startActivity(mainIntent);
            	                               
            	/* Finish splash activity so user can‘t go back to it. */
            	SplashScreenActivity.this.finish();
            	       
            	/* Apply our splash exit (fade out) and main
            	   entry (fade in) animation transitions. */
            	overridePendingTransition(R.anim.mainfadein, R.anim.splashfadeout);

            }

	    }, SPLASH_DISPLAY_LENGTH);
    }
}