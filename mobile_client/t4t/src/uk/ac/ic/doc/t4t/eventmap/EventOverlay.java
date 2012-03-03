package uk.ac.ic.doc.t4t.eventmap;

import java.util.ArrayList;

import uk.ac.ic.doc.t4t.EventDetailsActivity;
import uk.ac.ic.doc.t4t.EventListActivity;
import uk.ac.ic.doc.t4t.EventMapActivity;
import uk.ac.ic.doc.t4t.eventlist.EventItem;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.util.Log;

import com.google.android.maps.ItemizedOverlay;
import com.google.android.maps.OverlayItem;

public class EventOverlay extends ItemizedOverlay<EventOverlayItem> {
	private static final String TAG = EventOverlay.class.getSimpleName();
	private ArrayList<EventOverlayItem> mOverlays = new ArrayList<EventOverlayItem>();
	private Context context;
	
	public EventOverlay(Drawable defaultMarker, Context context) {
		super(boundCenterBottom(defaultMarker));
		this.context = context;
	}
	
	public void addOverlay(EventOverlayItem overlay) {
	    mOverlays.add(overlay);
	    populate();
	    Log.v(TAG, "Adding overlay item, currently have " + mOverlays.size() + " items");
	}

	@Override
	protected EventOverlayItem createItem(int i) {
		return mOverlays.get(i);
	}

	@Override
	public int size() {
		return mOverlays.size();
	}
	
	public void clearOverlays(){
		mOverlays = new ArrayList<EventOverlayItem>();
	}
	
	
	@Override
	protected boolean onTap(int index) {
		EventOverlayItem item = mOverlays.get(index);
//		AlertDialog.Builder dialog = new AlertDialog.Builder(mContext);
//		dialog.setTitle(item.getTitle());
//		dialog.setMessage(item.getSnippet());
//		dialog.show();
//		return true;
		
//		May need to subclass OverlayItem to have EventItem params
//		OverlayItem item = mOverlays.get(index);
//		EventItem currentItem = (EventItem) adapterView.getItemAtPosition(position);
//		
//		Log.i(TAG, "Opening event: " + currentItem.getTitle());
//		
		Intent i = new Intent(context, EventDetailsActivity.class);
		i.putExtra("EventDetails", item.getEventItem());
		context.startActivity(i);
		return true;
	}

}
