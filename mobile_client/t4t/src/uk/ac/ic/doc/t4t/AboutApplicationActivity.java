package uk.ac.ic.doc.t4t;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class AboutApplicationActivity extends Activity {
	private final static String TAG = "AboutApplicationActivity";

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
        setContentView(R.layout.about);
        
        TextView url = (TextView) findViewById(R.id.aboutURL);
        url.setOnClickListener(new View.OnClickListener() {
			
			@Override
			public void onClick(View v) {
				String url = "https://github.com/johnflan/Twitter-4-Traffic";
				Intent i = new Intent(Intent.ACTION_VIEW);
				i.setData(Uri.parse(url));
				startActivity(i);
				finish();
				
			}
		});
        
    }
}
