package uk.ac.ic.doc.t4t.common.services.data;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.UnknownHostException;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.conn.HttpHostConnectException;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.protocol.HTTP;

import android.util.Log;


public class HTTPRequester {
	private static final String TAG = HTTPRequester.class.getSimpleName();
	
	public static String httpGet(String url){
		Log.i(TAG, "(GET) Requesting: " + url);
		
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
        } catch (UnknownHostException e){
        	e.printStackTrace();
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        
        httpclient.getConnectionManager().shutdown();
		
		return response;
	}
	
	
	public static String httpPost(String url, String body) {
		Log.i(TAG, "(PUT) Requesting: " + url);
		
		String response = null;
		
		if (url.equals(""))
			return "";

		HttpClient httpclient = new DefaultHttpClient();
		HttpPost request = new HttpPost(url);
		
		StringEntity se;
		try {
			se = new StringEntity(body, HTTP.UTF_8);
			se.setContentType("application/json");  
			request.setHeader("Content-Type","application/json;charset=UTF-8");
			request.setEntity(se);  
			
		} catch (UnsupportedEncodingException e1) {
			Log.e(TAG, "Error adding POST body: " + e1.getMessage());
		}


		ResponseHandler<String> handler = new BasicResponseHandler();  
        try {  
			response = httpclient.execute(request, handler);

        } catch (HttpHostConnectException e) {
        	Log.e(TAG, "Error contacting server: " + e.getMessage());
        } catch (UnknownHostException e){
        	e.printStackTrace();
        } catch (ClientProtocolException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }
        
        httpclient.getConnectionManager().shutdown();
		
		return response;
	}

}
