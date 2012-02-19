package uk.ac.ic.doc.t4t.eventdetails;

import java.util.List;

import uk.ac.ic.doc.t4t.R;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;


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
	    TextView tweetText;
	    TextView tweetUserName;
	    TextView tweetAge;
	    ImageView tweetProfileImage;
	
	    try{
	    	tweetText = (TextView)view.findViewById(R.id.TweetText);
	    	tweetUserName = (TextView)view.findViewById(R.id.TweetUsername);
	    	tweetAge = (TextView)view.findViewById(R.id.TweetAge);
	    	tweetProfileImage = (ImageView) view.findViewById(R.id.TweetUserIcon);
	    	
	    } catch( ClassCastException e ) {
	    	Log.e(TAG, "Layout must provide an image and a text view with ID's icon and text.", e);
	    	throw e;
	    }
	
		TweetItem item = getItem(position);
		
		tweetText.setText(item.getMessageText());
		tweetUserName.setText(item.getAccountName());
		//tweetAge.setText()

	    return view;
	  }
}
