package uk.ac.ic.doc.t4t.eventlist;

import java.io.Serializable;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Date;

public class EventItem implements Serializable{

	private static final long serialVersionUID = 3305037298459804021L;
	
	private String eventID;
	private Date eventStartTime;
	
	private Date eventEndTime;
	
	private int eventType;
	private String category;
	private String severity;
	
	private Date lastModifiedTime;
	
	private String sector;
	private String location;
	private String title;
	private String description;
	
	private String postCodeStart;
	private String postCodeEnd;
	
	private String remark;
	private Date remarkTime;
	
	private double latitude;
	private double longitude;
	
	private double distanceFromEventKM;
	
	public String getEventID() {
		return eventID;
	}
	public void setEventID(String eventID) {
		this.eventID = eventID;
	}
	public Date getEventStartTime() {
		return eventStartTime;
	}
	public void setEventStartTime(Date eventStartTime) {
		this.eventStartTime = eventStartTime;
	}

	public Date getEventEndTime() {
		return eventEndTime;
	}
	public void setEventEndTime(Date eventEndTime) {
		this.eventEndTime = eventEndTime;
	}

	public int getEventType() {
		return eventType;
	}
	public void setEventType(int eventType) {
		this.eventType = eventType;
	}
	public String getCategory() {
		return category;
	}
	public void setCategory(String category) {
		this.category = category;
	}
	public String getSeverity() {
		return severity;
	}
	public void setSeverity(String severity) {
		this.severity = severity;
	}
	public Date getLastModifiedTime() {
		return lastModifiedTime;
	}
	public void setLastModifiedTime(Date lastModifiedTime) {
		this.lastModifiedTime = lastModifiedTime;
	}
	public String getLocation() {
		return location;
	}
	public void setLocation(String location) {
		this.location = location;
	}
	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getPostCodeStart() {
		return postCodeStart;
	}
	public void setPostCodeStart(String postCodeStart) {
		this.postCodeStart = postCodeStart;
	}
	public String getPostCodeEnd() {
		return postCodeEnd;
	}
	public void setPostCodeEnd(String postCodeEnd) {
		this.postCodeEnd = postCodeEnd;
	}
	public String getRemark() {
		return remark;
	}
	public void setRemark(String remark) {
		this.remark = remark;
	}
	public Date getRemarkTime() {
		return remarkTime;
	}
	public void setRemarkTime(Date remarkTime) {
		this.remarkTime = remarkTime;
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
	public String getSector() {
		return sector;
	}
	public void setSector(String sector) {
		this.sector = sector;
	}
	public void setCurrentDistanceFromEvent(double f) {
		BigDecimal bd = new BigDecimal(f).setScale(1, RoundingMode.HALF_EVEN);
		f = bd.doubleValue();
		distanceFromEventKM = f;
		
	}
	public double getCurrentDistanceFromEvent(){
		
		return distanceFromEventKM;
	}

}
