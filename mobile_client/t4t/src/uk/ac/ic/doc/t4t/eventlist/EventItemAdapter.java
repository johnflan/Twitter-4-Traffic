package uk.ac.ic.doc.t4t.eventlist;

import java.util.List;

import uk.ac.ic.doc.t4t.R;
import uk.ac.ic.doc.t4t.R.id;
import android.content.Context;
import android.graphics.drawable.Drawable;
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
		ImageView eventCategory;
	
	    view = inflater.inflate(resourceId, parent, false);
	
	    try {
	    	textTitle = (TextView)view.findViewById(R.id.eventTitle);
	    	textLocation = (TextView)view.findViewById(R.id.eventLocation);
	    	textDescription = (TextView)view.findViewById(R.id.eventDescription);
	    	eventCategory = (ImageView)view.findViewById(R.id.eventTypeIcon);
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Your layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	
		EventItem item = getItem(position);

	    textTitle.setText(item.getTitle());
	    textLocation.setText(item.getLocation());
	    textDescription.setText(item.getDescription());
	    
	    if (item.getCategory().equalsIgnoreCase("works"))
	    	eventCategory.setImageResource(R.drawable.sign_works);
	    else if (item.getCategory().equalsIgnoreCase("signal failure"))
	    	eventCategory.setImageResource(R.drawable.sign_signal_failure);
	    else if (item.getCategory().equalsIgnoreCase("accident"))
	    	eventCategory.setImageResource(R.drawable.sign_accident);
	    else
	    	eventCategory.setImageResource(R.drawable.sign_generic);
	    	
		
	    return view;
	  }
}
