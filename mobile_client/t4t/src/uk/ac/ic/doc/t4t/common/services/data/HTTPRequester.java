package uk.ac.ic.doc.t4t.common.services.data;

import java.io.IOException;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.conn.HttpHostConnectException;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;

import android.util.Log;


public class HTTPRequester {
	private static final String TAG = HTTPRequester.class.getSimpleName();
	
	public static String httpGet(String url){
		Log.i(TAG, "Requesting: " + url);
		
		String response = null;
		
		if (url.equals(""))
			return "";

		HttpClient httpclient = new DefaultHttpClient();
		HttpGet request = new HttpGet(url);

		ResponseHandler<String> handler = new BasicResponseHandler();  
        try {  
			response = httpclient.execute(request, handler);

        } catch (HttpHostConnectException e) {
        	Log.e(TAG, "Error contacting server: " + e.getMessage());
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        
        httpclient.getConnectionManager().shutdown();
		
		return response;
	}

}
