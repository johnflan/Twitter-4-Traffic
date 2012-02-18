package uk.ac.ic.doc.t4t.eventlist;

import java.util.List;

import uk.ac.ic.doc.t4t.R;
import uk.ac.ic.doc.t4t.R.id;
import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
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
	
	    view = inflater.inflate(resourceId, parent, false);
	
	    try {
	    	textTitle = (TextView)view.findViewById(R.id.eventTitle);
	    	textLocation = (TextView)view.findViewById(R.id.eventLocation);
	    	textDescription = (TextView)view.findViewById(R.id.eventDescription);
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Your layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	
		EventItem item = getItem(position);

	    textTitle.setText(item.getTitle());
	    textLocation.setText(item.getLocation());
	    textDescription.setText(item.getDescription());
		
	    return view;
	  }
}
