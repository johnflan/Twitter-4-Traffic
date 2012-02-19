package uk.ac.ic.doc.t4t.eventlist;

import java.util.List;

import uk.ac.ic.doc.t4t.R;
import uk.ac.ic.doc.t4t.R.id;
import android.content.Context;
import android.graphics.drawable.Drawable;
import android.location.Location;
import android.location.LocationManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;



public class EventItemAdapter extends ArrayAdapter<EventItem> {
	
	private final static String TAG = "EventItemAdapter";
	private int resourceId = 0;
	private LayoutInflater inflater;
	private Context context;

	public EventItemAdapter(Context context, int resourceId, List<EventItem> eventItems) {
		super(context, 0, eventItems);
	    this.resourceId = resourceId;
		inflater = (LayoutInflater)context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		this.context = context;
		//super.setNotifyOnChange(true);
	}
	
	@Override
	public View getView(int position, View convertView, ViewGroup parent) {
		View view;
		TextView textTitle;
		TextView textLocation;
		TextView textDescription;
		TextView textCurrentDistance;
		TextView textCurrentDistanceType;
		ImageView imageEventCategory;
		ImageView imageEventSeverity;
	
	    view = inflater.inflate(resourceId, parent, false);
	
	    try {
	    	textTitle = (TextView)view.findViewById(R.id.eventTitle);
	    	textLocation = (TextView)view.findViewById(R.id.eventLocation);
	    	textDescription = (TextView)view.findViewById(R.id.eventDescription);    	
	    	textCurrentDistance = (TextView)view.findViewById(R.id.eventDistance);
	    	textCurrentDistanceType = (TextView)view.findViewById(R.id.eventDistanceType);
	    	
	    	imageEventCategory = (ImageView)view.findViewById(R.id.eventTypeIcon);
	    	imageEventSeverity = (ImageView)view.findViewById(R.id.severityIcon);
	    	
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	
		EventItem item = getItem(position);

	    textTitle.setText(item.getTitle());
	    textLocation.setText(item.getLocation());
	    textDescription.setText(item.getDescription());
	    
	    //Distance from event, if we have no distance data hide section
	    if (item.getCurrentDistanceFromEvent() != 0){
	    	textCurrentDistance.setText( Double.toString(item.getCurrentDistanceFromEvent()) );
	    } else {
	    	textCurrentDistance.setText( "" );
	    	textCurrentDistanceType.setText( "" );
	    }
	    
	    //Event category icon
	    if (item.getCategory().equalsIgnoreCase("works"))
	    	imageEventCategory.setImageResource(R.drawable.sign_works);
	    else if (item.getCategory().equalsIgnoreCase("signal failure"))
	    	imageEventCategory.setImageResource(R.drawable.sign_signal_failure);
	    else if (item.getCategory().equalsIgnoreCase("accident"))
	    	imageEventCategory.setImageResource(R.drawable.sign_accident);
	    else
	    	imageEventCategory.setImageResource(R.drawable.sign_generic);
	    
	    //Event severity icon
	    //moderate is the most common, but may have severe or low (no icon for low)
	    if (item.getSeverity().equalsIgnoreCase("moderate"))
	    	imageEventSeverity.setImageResource(R.drawable.event_orange);
	    else if (item.getSeverity().equalsIgnoreCase("severe"))
	    	imageEventSeverity.setImageResource(R.drawable.event_red);
	    
	    return view;
	  }
}
