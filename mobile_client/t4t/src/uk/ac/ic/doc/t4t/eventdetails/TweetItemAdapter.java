package uk.ac.ic.doc.t4t.eventdetails;

import java.util.List;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;


public class TweetItemAdapter extends ArrayAdapter<TweetItem> {
	
	private final static String TAG = "TweetItemAdapter";
	private int resourceId = 0;
	private LayoutInflater inflater;
	private Context context;

	public TweetItemAdapter(Context context, int resourceId, List<TweetItem> tweetItems) {
		super(context, 0, tweetItems);
	    this.resourceId = resourceId;
		inflater = (LayoutInflater)context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		this.context = context;
		//super.setNotifyOnChange(true);
	}
	
	@Override
	public View getView(int position, View convertView, ViewGroup parent) {
		View view;

	
	    view = inflater.inflate(resourceId, parent, false);
	
	    try{
	    	
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	
		TweetItem item = getItem(position);

	   
	    
	    return view;
	  }
}
