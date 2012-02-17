package uk.ac.ic.doc.t4t;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;

public class SplashScreenActivity extends Activity {

	private final int SPLASH_DISPLAY_LENGTH = 1500;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.splash);

    	new Handler().postDelayed(new Runnable(){
    		 
            @Override
            public void run() {

                /* Create an Intent that will start the Menu-Activity. */
            	Intent mainIntent = new Intent(SplashScreenActivity.this, EventListActivity.class);
            	SplashScreenActivity.this.startActivity(mainIntent);
            	                               
            	/* Finish splash activity so user cant go back to it. */
            	SplashScreenActivity.this.finish();
            	       
            	/* Apply our splash exit (fade out) and main
            	   entry (fade in) animation transitions. */
            	overridePendingTransition(R.anim.mainfadein, R.anim.splashfadeout);

            }

	    }, SPLASH_DISPLAY_LENGTH);
    }
}