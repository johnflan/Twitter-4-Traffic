package ic.zhg.test;


import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;

public class Main extends Activity {
    
	String URL_radius = "http://vm-project-g1153006.doc.ic.ac.uk:55003/t4t/0.1/disruptions?latitude=2.3&longitude=2.1&radius=10";
	private Button btn;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        btn = (Button)findViewById(R.id.rbtn);
        
        
        btn.setOnClickListener(new OnClickListener(){
			public void onClick(View v) 
			{
				RestClient client = new RestClient();
				client.connect(URL_radius);
				String text = client.result;
				Intent intent = new Intent();
				intent.setClass(Main.this, List.class);
				intent.putExtra("result",text);
				startActivity(intent);	
				
			}});
    }
    
        
}