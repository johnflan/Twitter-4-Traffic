package uk.ac.ic.doc.t4t;

import java.util.ArrayList;
import java.util.List;
import uk.ac.ic.doc.t4t.common.services.DataMgr;
import uk.ac.ic.doc.t4t.common.services.TrafficCameraImageDownloader;
import uk.ac.ic.doc.t4t.eventdetails.TweetItem;
import uk.ac.ic.doc.t4t.eventdetails.TweetItemAdapter;
import uk.ac.ic.doc.t4t.eventlist.EventItem;
import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
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
	private ImageView trafficCameras;
	private Dialog dialog;
	private EventItem eventDetails;
	private int displayTrafficImage = 0;
	private TrafficCameraImageDownloader downloader;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.eventdetails);
        tweetList = (ListView) findViewById(R.id.tweetList);
        trafficCameras = (ImageView) findViewById(R.id.eventTrafficCameras);
        
    	Bundle extras = getIntent().getExtras();
    	
    	if(extras !=null) {
    		eventDetails = (EventItem) extras.getSerializable("EventDetails");
    		populateEvent(eventDetails);
    	} else {
    		return;
    	}
    	
    	reportEventBtn = (ImageButton) findViewById(R.id.header_share_button);
        reportEventBtn.setOnClickListener(new View.OnClickListener() {	
			@Override
			public void onClick(View v) {
				Log.i(TAG, "Opening report event activity");
				
				Intent i = new Intent(EventDetailsActivity.this, ReportQuickEventActivity.class);
				startActivity(i);	
			}
		});
        
        trafficCameras.setOnClickListener(new View.OnClickListener() {
			
			@Override
			public void onClick(View v) {
				displayTrafficCamera();
			}
		});

        tweetList.setAdapter(new TweetItemAdapter(this, R.layout.tweetitem, tweets));
    	new FetchTweets(this).execute(eventDetails);
    }


	private void populateEvent(EventItem eventDetails) {
		
		TextView textTitle;
		TextView textLocation;
		TextView textDescription;
		TextView textCurrentDistance;
		TextView textCurrentDistanceType;
		ImageView imageEventCategory;
		ImageView imageEventSeverity;
		ImageView imageTrafficCamera;

		try {
	    	textTitle = (TextView) findViewById(R.id.eventTitle);
	    	textLocation = (TextView) findViewById(R.id.eventLocation);
	    	textDescription = (TextView) findViewById(R.id.eventDescription);    	
	    	textCurrentDistance = (TextView) findViewById(R.id.eventDistance);
	    	textCurrentDistanceType = (TextView) findViewById(R.id.eventDistanceType);
	    	
	    	imageEventCategory = (ImageView) findViewById(R.id.eventTypeIcon);
	    	imageEventSeverity = (ImageView) findViewById(R.id.severityIcon);
	    	
	    	imageTrafficCamera = (ImageView) findViewById(R.id.eventTrafficCameras);
	    	
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
	    	textCurrentDistanceType.setText( "km" );
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
	    
	    Log.v(TAG, "Number of traffic cameras " + eventDetails.getTrafficCameras().size());
	    
	    if (eventDetails.getTrafficCameras().size() == 0)
	    	imageTrafficCamera.setVisibility(View.INVISIBLE);

	    	
	}
	
	private void displayTrafficCamera(){
		
		if (eventDetails == null)
        	return;
		
		downloader = new TrafficCameraImageDownloader();	
		Log.i(TAG, "Displaying traffic camera images");

		dialog = new Dialog(EventDetailsActivity.this);
		dialog.requestWindowFeature(dialog.getWindow().FEATURE_NO_TITLE);
        dialog.setContentView(R.layout.event_details_traffic_cam_imageview_popup);
        dialog.setCancelable(true);
        
        Log.i(TAG, "Displaying URL " + eventDetails.getTrafficCameras().get(0).getLink());
        
        dialog.show();
        
        ImageView imageView = (ImageView) dialog.findViewById(R.id.trafficCameraImage);
        TextView caption = (TextView) dialog.findViewById(R.id.cameraCountText);
        
        String captionText = (displayTrafficImage + 1)  + " of " +  eventDetails.getTrafficCameras().size() + " traffic cameras";
        caption.setText(captionText);
        
        downloader.download(eventDetails.getTrafficCameras().get(displayTrafficImage).getLink(), imageView);
        
        imageView.setOnClickListener(new View.OnClickListener() {
			
			@Override
			public void onClick(View v) {
				getNextTrafficCamera();				
			}
		});
        
	}
	
	private void getNextTrafficCamera(){
		
		if (eventDetails.getTrafficCameras().size() == 1)
			return;
		
		displayTrafficImage++;
		
		if (displayTrafficImage >= eventDetails.getTrafficCameras().size())
			displayTrafficImage = 0;
		
		ImageView imageView = (ImageView) dialog.findViewById(R.id.trafficCameraImage);
		TextView caption = (TextView) dialog.findViewById(R.id.cameraCountText);
		
		downloader.download(eventDetails.getTrafficCameras().get(displayTrafficImage).getLink(), imageView);
		
		String captionText = (displayTrafficImage + 1) + " of " +  eventDetails.getTrafficCameras().size() + " traffic cameras";
        caption.setText(captionText);
	}
	
	private class FetchTweets extends AsyncTask<EventItem, Void, List<TweetItem>>{

		private Context context;
		private DataMgr restClient;
		
		public FetchTweets(Context context){
			this.context = context;
			restClient = new DataMgr(context);
		}

		
		@Override
		protected List<TweetItem> doInBackground(EventItem... params) {
			params[0].getEventID();
			return restClient.requestTweets(eventDetails.getEventID());
		}
		
		@Override
	    protected void onPostExecute(List<TweetItem> newTweets) {
	        
	        tweets.clear();
			
	        Log.i(TAG, "Adding " + newTweets.size() + " new tweets to listView");
			if (newTweets != null && newTweets.size() > 0){
				tweets.addAll(newTweets);	
			} else {
//				TweetItem item = new TweetItem();
//				item.setMessageText("No tweets found");
//				tweets.add(item);
			}
				
			tweetList.setAdapter(new TweetItemAdapter(context, R.layout.tweetitem, tweets));
			
			
	        super.onPostExecute(newTweets);

	    }
		
	}
}
