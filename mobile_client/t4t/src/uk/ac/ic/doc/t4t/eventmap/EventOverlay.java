package uk.ac.ic.doc.t4t.eventmap;

import java.util.ArrayList;

import uk.ac.ic.doc.t4t.EventDetailsActivity;
import uk.ac.ic.doc.t4t.EventListActivity;
import uk.ac.ic.doc.t4t.eventlist.EventItem;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.util.Log;

import com.google.android.maps.ItemizedOverlay;
import com.google.android.maps.OverlayItem;

public class EventOverlay extends ItemizedOverlay<OverlayItem> {
	
	private ArrayList<OverlayItem> mOverlays = new ArrayList<OverlayItem>();
	private Context mContext;
	
	public EventOverlay(Drawable defaultMarker, Context context) {
		super(boundCenterBottom(defaultMarker));
		mContext = context;
	}
	
	public void addOverlay(OverlayItem overlay) {
	    mOverlays.add(overlay);
	    populate();
	}

	@Override
	protected OverlayItem createItem(int i) {
		return mOverlays.get(i);
	}

	@Override
	public int size() {
		return mOverlays.size();
	}
	
	@Override
	protected boolean onTap(int index) {
		OverlayItem item = mOverlays.get(index);
		AlertDialog.Builder dialog = new AlertDialog.Builder(mContext);
		dialog.setTitle(item.getTitle());
		dialog.setMessage(item.getSnippet());
		dialog.show();
		return true;
		
//		May need to subclass OverlayItem to have EventItem params
//		OverlayItem item = mOverlays.get(index);
//		EventItem currentItem = (EventItem) adapterView.getItemAtPosition(position);
//		
//		Log.i(TAG, "Opening event: " + currentItem.getTitle());
//		
//		Intent i = new Intent(EventListActivity.this, EventDetailsActivity.class);
//		i.putExtra("EventDetails", currentItem);
//		startActivity(i);
//		return true;
	}

}
