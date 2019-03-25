package gq.yigit.mycity.tools;

import android.net.wifi.WifiConfiguration;
import android.os.AsyncTask;
import android.util.Log;
import cz.msebera.android.httpclient.HttpResponse;
import cz.msebera.android.httpclient.HttpVersion;
import cz.msebera.android.httpclient.NameValuePair;
import cz.msebera.android.httpclient.client.HttpClient;
import cz.msebera.android.httpclient.client.entity.UrlEncodedFormEntity;
import cz.msebera.android.httpclient.client.methods.HttpGet;
import cz.msebera.android.httpclient.client.methods.HttpPost;

import cz.msebera.android.httpclient.conn.ClientConnectionManager;
import cz.msebera.android.httpclient.conn.scheme.PlainSocketFactory;
import cz.msebera.android.httpclient.conn.scheme.Scheme;
import cz.msebera.android.httpclient.conn.scheme.SchemeRegistry;
import cz.msebera.android.httpclient.conn.ssl.SSLSocketFactory;
import cz.msebera.android.httpclient.impl.client.DefaultHttpClient;
import cz.msebera.android.httpclient.impl.client.HttpClientBuilder;
import cz.msebera.android.httpclient.impl.conn.tsccm.ThreadSafeClientConnManager;
import cz.msebera.android.httpclient.message.BasicNameValuePair;
import cz.msebera.android.httpclient.params.BasicHttpParams;
import cz.msebera.android.httpclient.params.HttpParams;
import cz.msebera.android.httpclient.params.HttpProtocolParams;
import cz.msebera.android.httpclient.protocol.HTTP;
import gq.yigit.mycity.MainActivity;
import gq.yigit.mycity.R;

import javax.net.ssl.*;
import java.io.*;
import java.security.KeyStore;
import java.util.*;

public class WebRequest extends AsyncTask<Void,Void,String> {
	private String url;
	private HashMap<String,String> request_content;
	private boolean request_type;//True = GET, False = POST

	private HttpClient client;
	private HttpGet get_request;
	private HttpPost post_request;
	private HttpResponse response;
	private List<responseListener> listeners = new ArrayList<>();


	public WebRequest(String url, boolean request_type, HashMap<String,String> request_content){

		client = getNewHttpClient();

		this.url = url;
		this.request_content = request_content;
		this.request_type = request_type;

		if(request_type){

			Iterator iterator = request_content.entrySet().iterator();
			this.url += "?";

			while(iterator.hasNext()){
				Map.Entry pair = (Map.Entry)iterator.next();
				this.url += pair.getKey() + "=" + pair.getValue() + "&";
				iterator.remove();
			}
			get_request = new HttpGet(this.url);
		}else{
			post_request = new HttpPost(this.url);
		}
	}

	protected String doInBackground(Void... params){
		if(!request_type){
			try {
				post_request = new HttpPost(url);
				List<NameValuePair> pairs = new ArrayList<>(request_content.size());

				Iterator iterator = request_content.entrySet().iterator();

				while (iterator.hasNext()) {
					Map.Entry pair = (Map.Entry) iterator.next();
					pairs.add(new BasicNameValuePair(pair.getKey().toString(), pair.getValue().toString()));
					iterator.remove();
				}
				post_request.setEntity(new UrlEncodedFormEntity(pairs));
				response = client.execute(post_request);
			}catch (Exception e){
				Log.e("[ERROR](request:67): ", e.toString());
			}
		}else{
			try {
				response = client.execute(get_request);
			}catch (Exception e){
				Log.e("[ERROR](request:74): ", e.toString());
			}
		}
		try {
			BufferedReader rd = new BufferedReader
					(new InputStreamReader(
							response.getEntity().getContent()));
			String line = "";
			String temp;
			while ((temp = rd.readLine()) != null) {
				line += temp;
			}
			return line;
		}catch(Exception e){
			Log.e("[ERROR](request:87): ", e.toString());
		}
		return "Error";
	}
	protected void onPostExecute(String result){
		for (responseListener hl : listeners)
			hl.receivedResponse(!result.equals("Error"),result);
	}

	public void addListener(responseListener toAdd) {
		listeners.add(toAdd);
	}
	public HttpClient getNewHttpClient() {
		try {
			KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
			trustStore.load(null, null);

			MySSLSocketFactory sf = new MySSLSocketFactory(trustStore);
			sf.setHostnameVerifier(SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER);

			HttpParams params = new BasicHttpParams();
			HttpProtocolParams.setVersion(params, HttpVersion.HTTP_1_1);
			HttpProtocolParams.setContentCharset(params, HTTP.UTF_8);

			SchemeRegistry registry = new SchemeRegistry();
			registry.register(new Scheme("http", PlainSocketFactory.getSocketFactory(), 5000));
			registry.register(new Scheme("https", sf, 5000));

			ClientConnectionManager ccm = new ThreadSafeClientConnManager(params, registry);

			return new DefaultHttpClient(ccm, params);
		} catch (Exception e) {
			return new DefaultHttpClient();
		}
	}
}


