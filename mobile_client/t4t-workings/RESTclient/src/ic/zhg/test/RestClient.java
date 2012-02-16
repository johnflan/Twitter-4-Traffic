package ic.zhg.test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


import android.util.Log;

public class RestClient {
	
	public static String result;
	
	private static String convertStreamToString(InputStream is){
		BufferedReader reader = new BufferedReader(new InputStreamReader(is));
		StringBuilder sb = new StringBuilder();
		String line = null;
		try{
			while ((line = reader.readLine()) != null){
				sb.append(line+"\n");
			}
		} catch (IOException e){
			e.printStackTrace();
		} finally {
			try {
				is.close();
			} catch (IOException e){
				e.printStackTrace();
			}
		}
		return sb.toString();
	}
	
	public static void connect (String url){
		HttpClient httpclient = new DefaultHttpClient();
		HttpGet httpget = new HttpGet(url);
		HttpResponse response;
		try{
			response = httpclient.execute(httpget);			
			Log.i("WOW",response.getStatusLine().toString());
			HttpEntity entity = response.getEntity();
			
			if(entity != null){
				InputStream instream = entity.getContent();
				result = convertStreamToString(instream);
				
				JSONObject jObject = new JSONObject(result);
				JSONArray dsrptArray = jObject.getJSONArray("disruptions");
				
				
				for(int i=0; i<dsrptArray.length(); i++)
				{
					int n = i+1;
					Log.i("WOW","<disruption"+n+">\n"+dsrptArray.getJSONObject(i).getString("eventID").toString()
							+dsrptArray.getJSONObject(i).getString("location").toString());
				}
				instream.close();				
			} 
		}catch (ClientProtocolException e){
			e.printStackTrace();
		}catch (IOException e){
			e.printStackTrace();
		}catch (JSONException e){
			e.printStackTrace();
		}			
	}
}
