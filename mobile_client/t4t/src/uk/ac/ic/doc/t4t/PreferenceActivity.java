package uk.ac.ic.doc.t4t;

import uk.ac.ic.doc.t4t.common.PreferencesHelper;
import android.os.Bundle;

public class PreferenceActivity extends android.preference.PreferenceActivity {
	
	@Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
 
        getPreferenceManager().setSharedPreferencesName(
        		PreferencesHelper.PREFS_NAME);
        addPreferencesFromResource(R.xml.preferences);
    }

}
