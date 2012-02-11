package ic.zhg.test;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.ListActivity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;

public class List extends ListActivity{
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
		
		Intent intent=getIntent();
		String result=intent.getStringExtra("result");
		
	
		JSONObject jObject;
		try {
			jObject = new JSONObject(result);
			JSONArray dsrptArray = jObject.getJSONArray("disruptions");
			ArrayList values = new ArrayList();
			for(int i=0; i<dsrptArray.length(); i++)
			{
				int n = i+1;
				
				Log.i("WOW","<disruption"+n+">\n"+dsrptArray.getJSONObject(i).getString("eventID").toString()
						+dsrptArray.getJSONObject(i).getString("location").toString());
				values.add(dsrptArray.getJSONObject(i).getString("eventID").toString());
			}
			ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1,values);
			setListAdapter(adapter);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
	}
}