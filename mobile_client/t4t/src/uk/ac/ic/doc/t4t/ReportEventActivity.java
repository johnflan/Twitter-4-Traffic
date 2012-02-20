package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;

import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import android.app.Activity;
import android.os.Bundle;
import android.widget.ListView;

public class ReportEventActivity extends Activity {
	private final static String TAG = "ReportEventsActivity";

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.reportevent);
        
    }
    
}
