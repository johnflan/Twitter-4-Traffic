package ic.zhg.test;

import java.util.ArrayList;
import java.util.List;

import com.google.android.maps.GeoPoint;
import com.google.android.maps.ItemizedOverlay;
import com.google.android.maps.MapActivity;
import com.google.android.maps.MapView;
import com.google.android.maps.MyLocationOverlay;
import com.google.android.maps.OverlayItem;

import android.graphics.Point;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

public class MapLocationActivity extends MapActivity {
    private MapView map=null;
    private MyLocationOverlay me = null;
    
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        map = (MapView)findViewById(R.id.map);
        
        map.getController().setCenter(getPoint(51.498270,-0.177583));
        map.getController().setZoom(17);
        map.setBuiltInZoomControls(true);
        
        Drawable marker=getResources().getDrawable(R.drawable.marker);
        
        marker.setBounds(0, 0, marker.getIntrinsicWidth(), marker.getIntrinsicHeight());
        
        map.getOverlays().add(new SitesOverlay(marker));
        
        me = new MyLocationOverlay(this,map);
        map.getOverlays().add(me);
    }
    
    public void onResume(){
    	super.onResume();
    	me.enableCompass();
    }
    
    public void onPause() {
    	super.onPause();
    	me.disableCompass();
    }
    
    protected boolean isRouteDisplayed() {
    	return (true);
    }

	private GeoPoint getPoint(double lat, double lon) {
		return(new GeoPoint((int)(lat*1000000.0),(int)(lon*1000000.0)));
		
	}
	
	private class SitesOverlay extends ItemizedOverlay<OverlayItem> {
		private List<OverlayItem> items = new ArrayList<OverlayItem>();
		private Drawable marker = null;
		private PopupPanel panel = new PopupPanel (R.layout.popup);
		
		public SitesOverlay(Drawable marker) {
			super(marker);
			this.marker = marker;
			items.add(new OverlayItem(getPoint(40.748963,-73.96586221),"UN","United Nations"));
			items.add(new OverlayItem(getPoint(40.76866299974387,-73.98268461227417),"Lincoln Center","Home of Jazz at Lincoln Center"));
			populate();
		}
		
		@Override
		protected boolean onTap(int i) {
			OverlayItem item = getItem(i);
			GeoPoint geo = item.getPoint();
			Point pt = map.getProjection().toPixels(geo, null);
			View view = panel.getView();
			
			((TextView)view.findViewById(R.id.latitude)).setText(String.valueOf(geo.getLatitudeE6()/1000000.0));
	        ((TextView)view.findViewById(R.id.longitude)).setText(String.valueOf(geo.getLongitudeE6()/1000000.0));
	        ((TextView)view.findViewById(R.id.x)).setText(String.valueOf(pt.x));
	        ((TextView)view.findViewById(R.id.y)).setText(String.valueOf(pt.y));
	        
	        panel.show(pt.y*2>map.getHeight());
	        
	        return (true);
		}


		@Override
		protected OverlayItem createItem(int i) {
			return(items.get(i));
		}


		@Override
		public int size() {
			return (items.size());
		}
		
		class PopupPanel {
			View popup;
			boolean isVisible = false;
			
			PopupPanel(int layout) {
				ViewGroup parent = (ViewGroup)map.getParent();
				popup = getLayoutInflater().inflate(layout, parent, false);
				popup.setOnClickListener(new View.OnClickListener() {
					public void onClick(View v) {
						hide();						
					}
				});
			}
			
			View getView() {
				return(popup);
			}
			
			void show(boolean alignTop){
				RelativeLayout.LayoutParams lp = new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT,RelativeLayout.LayoutParams.WRAP_CONTENT);
				if(alignTop) {
					lp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
					lp.setMargins(0, 20, 0, 0);
				}
				else {
					lp.addRule(RelativeLayout.ALIGN_BOTTOM);
					lp.setMargins(0, 0, 0, 60);
				}			
				hide();
				
				((ViewGroup)map.getParent()).addView(popup, lp);
				isVisible = true;
			}
			
			void hide() {
				if (isVisible) {
					isVisible = false;
					((ViewGroup)popup.getParent()).removeView(popup);
				}
			}
		}
		
		
	}
}