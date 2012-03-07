package uk.ac.ic.doc.t4t.eventlist;

import java.io.Serializable;
import java.net.URLDecoder;

public class TrafficCamera implements Serializable, Cloneable {

	private static final long serialVersionUID = -6888330858904536660L;
	
	private String link;
	private String title;
	private double latitude;
	private double longitude;
	
	public String getLink() {
		return link;
	}
	public void setLink(String link) {
		this.link = URLDecoder.decode( link );
	}
	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}
	public double getLatitude() {
		return latitude;
	}
	public void setLatitude(double latitude) {
		this.latitude = latitude;
	}
	public double getLongitude() {
		return longitude;
	}
	public void setLongitude(double longitude) {
		this.longitude = longitude;
	}
	
}
