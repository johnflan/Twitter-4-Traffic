package ic.zhg.test.tweet;

import java.text.DateFormat;
import java.util.Date;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;




public class TweetTest extends Activity {
	
	protected EditText message;
	protected Button tweetBtn;
	
	
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        message = (EditText) findViewById (R.id.input_text);
        tweetBtn = (Button) findViewById (R.id.tweet_button);
        
        tweetBtn.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				String currentDateTimeString = DateFormat.getDateInstance().format(new Date());
				String text = message.getText().toString()+" #T4T"+" at " + currentDateTimeString;
				
				Intent intent =new Intent(Intent.ACTION_SEND);
				intent.putExtra(Intent.EXTRA_TEXT, text);
				intent.setType("application/twitter");
				try{
					startActivity(Intent.createChooser(intent,null));
				}
				catch (ActivityNotFoundException e) {
				}
			}});
        
    }
}