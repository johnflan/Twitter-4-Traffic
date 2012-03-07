package uk.ac.ic.doc.t4t.eventdetails;

public class TweetItem {
	
	private String tweetID;
	private String accountName;
	private String realName;
	private String createdAt;
	private String accountLocation;
	private String messageText;
	private double latitude;
	private double longitude;
	private String tweetAge;
	private double ranking;
	
	public long getTweetID() {
		return Long.parseLong(tweetID);
	}
	public void setTweetID(String tweetID) {
		this.tweetID = tweetID;
	}
	public String getAccountName() {
		return accountName;
	}
	public void setAccountName(String accountName) {
		this.accountName = accountName;
	}
	public String getRealName() {
		return realName;
	}
	public void setRealName(String realName) {
		this.realName = realName;
	}
	public String getCreatedAt() {
		return createdAt;
	}
	public void setCreatedAt(String createdAt) {
		this.createdAt = createdAt;
	}
	public String getAccountLocation() {
		return accountLocation;
	}
	public void setAccountLocation(String accountLocation) {
		this.accountLocation = accountLocation;
	}
	public String getMessageText() {
		return messageText;
	}
	public void setMessageText(String messageText) {
		this.messageText = messageText;
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
	
	public String getTweetAge(){
		return tweetAge;
	}
	
	public void setTweetAge(String tweetAge){
		this.tweetAge = tweetAge;
	}

	public void setRanking(double rank){
		this.ranking = rank;
	}
	
	public double getRanking(){
		return this.ranking;
	}
}
