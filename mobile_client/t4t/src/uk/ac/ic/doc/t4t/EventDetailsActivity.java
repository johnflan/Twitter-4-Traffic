package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;

import uk.ac.ic.doc.t4t.common.services.RESTClient;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventdetails.TweetItemAdapter;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import uk.ac.ic.doc.t4t.eventlist.EventItemAdapter;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;

public class EventDetailsActivity extends Activity {

	private final static String TAG = "EventDetailsActivity";
	private List<TweetItem> tweets = new ArrayList<TweetItem>();
	private ListView tweetList;
	private ImageButton reportEventBtn;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.eventdetails);
        tweetList = (ListView)findViewById(R.id.tweetList);
        
    	Bundle extras = getIntent().getExtras();
    	EventItem eventDetails = null;
    	if(extras !=null) {
    		eventDetails = (EventItem) extras.getSerializable("EventDetails");
    	}
    	
    	reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventDetailsActivity.this, ReportEventActivity.class);
				startActivity(i);	
			}
		});
    	
    	populateEvent(eventDetails);  	
    	populateTweets(eventDetails);
    }

	private void populateTweets(EventItem eventDetails) {

		RESTClient restClient = new RESTClient(this);
		tweets = restClient.requestTweets(eventDetails.getEventID());
		if (tweets != null){
			tweetList.setAdapter(new TweetItemAdapter(this, R.layout.tweetitem, tweets));
		} else {
			
			//No tweets found
		}
			
        //tweetList.setClickable(true);
		
	}

	private void populateEvent(EventItem eventDetails) {
		
		TextView textTitle;
		TextView textLocation;
		TextView textDescription;
		TextView textCurrentDistance;
		TextView textCurrentDistanceType;
		ImageView imageEventCategory;
		ImageView imageEventSeverity;

		try {
	    	textTitle = (TextView) findViewById(R.id.eventTitle);
	    	textLocation = (TextView) findViewById(R.id.eventLocation);
	    	textDescription = (TextView) findViewById(R.id.eventDescription);    	
	    	textCurrentDistance = (TextView) findViewById(R.id.eventDistance);
	    	textCurrentDistanceType = (TextView) findViewById(R.id.eventDistanceType);
	    	
	    	imageEventCategory = (ImageView) findViewById(R.id.eventTypeIcon);
	    	imageEventSeverity = (ImageView) findViewById(R.id.severityIcon);
	    	
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	

	    textTitle.setText(eventDetails.getTitle());
	    textLocation.setText(eventDetails.getLocation());
	    textDescription.setText(eventDetails.getDescription());
	    
	    //Distance from event, if we have no distance data hide section
	    if (eventDetails.getCurrentDistanceFromEvent() != 0){
	    	textCurrentDistance.setText( Double.toString(eventDetails.getCurrentDistanceFromEvent()) );
	    } else {
	    	textCurrentDistance.setText( "" );
	    	textCurrentDistanceType.setText( "" );
	    }
	    
	    //Event category icon
	    if (eventDetails.getCategory().equalsIgnoreCase("works"))
	    	imageEventCategory.setImageResource(R.drawable.sign_works);
	    else if (eventDetails.getCategory().equalsIgnoreCase("signal failure"))
	    	imageEventCategory.setImageResource(R.drawable.sign_signal_failure);
	    else if (eventDetails.getCategory().equalsIgnoreCase("accident"))
	    	imageEventCategory.setImageResource(R.drawable.sign_accident);
	    else
	    	imageEventCategory.setImageResource(R.drawable.sign_generic);
	    
	    //Event severity icon
	    //moderate is the most common, but may have severe or low (no icon for low)
	    if (eventDetails.getSeverity().equalsIgnoreCase("moderate"))
	    	imageEventSeverity.setImageResource(R.drawable.event_orange);
	    else if (eventDetails.getSeverity().equalsIgnoreCase("severe"))
	    	imageEventSeverity.setImageResource(R.drawable.event_red);
	}
}
