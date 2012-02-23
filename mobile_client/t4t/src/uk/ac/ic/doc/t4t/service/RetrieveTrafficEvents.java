package uk.ac.ic.doc.t4t.service;

import uk.ac.ic.doc.t4t.UpdaterService;
import android.util.Log;

public class RetrieveTrafficEvents extends Thread {
	private static final String TAG = UpdaterService.class.getSimpleName();
	
	static final long DELAY = 30000;
	private boolean isRunning = false;
	
	public RetrieveTrafficEvents(){
		super("Retrieve traffic events");
	}
	
	public void run(){
		
		while (isRunning) {
			Log.d(TAG, "running thread");
			
			
			String data = "create some thread data";
			
			
			//Sleep
			try {
				Thread.sleep(DELAY);
			} catch (InterruptedException e) {
				//Interrupted
				isRunning = false;
			}
		} //while
		
	}
	
	public boolean isRunning(){
		return this.isRunning;
	}

}
