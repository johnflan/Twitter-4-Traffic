package uk.ac.ic.doc.t4t;

import android.app.Activity;
import android.os.Bundle;

public class EventMapActivity extends Activity {
	private final static String TAG = "EventMapActivity";

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.eventmap);
        
    }
}
