package uk.ac.ic.doc.t4t;

import com.google.android.maps.MapActivity;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;

public class EventMapActivity extends MapActivity {
	private final static String TAG = "EventMapActivity";
	private ImageButton reportEventBtn;

	@Override
	protected boolean isRouteDisplayed() {
		// TODO Auto-generated method stub
		return false;
	}

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.eventmap);
        
        reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventMapActivity.this, ReportEventActivity.class);
				startActivity(i);	
			}
		});
        
    }
	

}
