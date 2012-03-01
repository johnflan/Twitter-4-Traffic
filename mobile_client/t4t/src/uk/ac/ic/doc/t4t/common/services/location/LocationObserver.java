package uk.ac.ic.doc.t4t.common.services.location;

public interface LocationObserver {
	
	public void notifyLocationUpdate(double latitude, double longitude);

}
