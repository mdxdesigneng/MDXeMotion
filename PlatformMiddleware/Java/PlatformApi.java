import java.io.BufferedReader;
import java.util.concurrent.locks.Lock;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

/*
 * Module defining interface and methods to the middleware server
 * message received on a thread are parsed and queued for handling by the main module
 */

public class PlatformApi extends Thread {
	
	public abstract class msgFields {
		public boolean isRaw;
		public float v[];
		public msgFields() {
		   v = new float[6];
		}	
	}
	
	public class rawMsg extends msgFields {
		public rawMsg() {isRaw = true;}
	}

	public class xyzMsg extends msgFields {
		public xyzMsg() {isRaw = false;}
		
		float getX()    { return v[0]; }
		float getY()    { return v[1]; } 
		float getZ()    { return v[2]; } 
		float getRoll() { return v[3]; } 
		float getPitch(){ return v[4]; } 
		float getYaw()  { return v[5]; } 
		
		void setX(float val)    { v[0] = val; }
		void setY(float val)    { v[1] = val; } 
		void setZ(float val)    { v[2] = val; } 
		void setRoll(float val) { v[3] = val; } 
		void setPitch(float val){ v[4] = val; } 
		void setYaw(float val)  { v[5] = val; } 
	}

	private static class config {
		float gainX     = (float) 1.0; // factor for x values
		float gainY     = (float) 1.0; // factor for y values
		float gainZ     = (float) 1.0; // factor for z values
		float gainRoll  = (float) 1.0; // factor for roll values
		float gainPitch = (float) 1.0; // factor for pitch values
		float gainYaw   = (float) 1.0; // factor for yaw values
		float gain      = (float) 1.0; // factor for all values

		float washoutX     = (float) 1.0; // washout factor for x values
		float washoutY     = (float) 1.0; // washout factor for y values
		float washoutZ     = (float) 0.996; // washout factor for z values
		float washoutRoll  = (float) 0.996; // washout factor for roll values
		float washoutPitch = (float) 0.996; // washout factor for pitch values
		float washoutYaw   = (float) 0.996; // washout factor for yaw values
	}

	private final int MIDDLEWARE_PORT = 10002;
	private final Lock lock;
	ServerSocket middlewareServer;
	static config cfg;
	BufferedReader reader;
	JSONArray values = new JSONArray();
	
	private static final int INACTIVITY_TIMEOUT = 2000; // message interval to reset initial conditions
	private long prevMsgTime=0;
	static float washedYaw=0;
	static float prevYaw = 999; // a magic number used to detect first actual msg
	static float washedZAccel=0;
	static float prevZAccel=0;

	public PlatformApi(Lock l) {
		this.start();
		this.lock = l;
	}

	void begin() {
		cfg = new config();
		
	}

	void end() {
		try {
			middlewareServer.close();
		} catch (IOException e) {
			System.err.println(e);
		}
	}
	
	void resetShaping() {
		prevYaw = 999;  // a magic number used to detect first actual msg
		washedYaw=0;
		prevZAccel=0;
		washedZAccel=0;
	}
	
	public  xyzMsg createTestMsg( float x,float y, float z) {
		    xyzMsg msg = new xyzMsg();		
			
		    msg.setX(x); 
		    msg.setY(y); 
		    msg.setZ(z); 
		    return msg;		
	}
	
	public static xyzMsg shapeData(xyzMsg msg) {
	    msg.setX( msg.getX() * cfg.gainX * cfg.gain);
	    msg.setY( msg.getY() * cfg.gainY * cfg.gain);
	    msg.setZ( msg.getZ() * cfg.gainZ * cfg.gain);
	    msg.setRoll( msg.getRoll() * cfg.gainRoll * cfg.gain);
	    msg.setPitch(msg.getPitch() * cfg.gainPitch * cfg.gain);
	    msg.setYaw(msg.getYaw() * cfg.gainYaw *cfg.gain);
	    
	    // calculate washout	 	
	    if( prevYaw > 900)
	    	prevYaw = msg.getYaw(); // sets yaw to 0 at startup
	    float yawDelta = msg.getYaw() - prevYaw ;
	    if ( yawDelta < -1 ) yawDelta += 2 ;
	    if ( yawDelta > 1 ) yawDelta -= 2 ; 
	    washedYaw = cfg.washoutYaw * ( washedYaw + yawDelta );
	    //System.out.format("yaw washout- msg:%f, delta:%f, washed:%f\n",msg.yaw, yawDelta, washedYaw);	
	    prevYaw =  msg.getYaw();
	    msg.setYaw( washedYaw);
	    return msg;
	}

	float getOptionalField(JSONObject jsonObj, String field, float val) {
      try{
		System.out.print(field);
		String s = jsonObj.get(field).toString();
		
		if (s != null) {
			System.out.format(" %s ", s);
			val = Float.valueOf(s).floatValue();
			System.out.println(val);
		}
      }
      catch(Exception e ){
    	  System.out.println(e.toString());
      }
	 return val;
	}

	void parseRaw(boolean isNormalized, JSONArray values) {
		// System.out.print(" parseRaw "); System.out.println( values);
		if (isNormalized) { // for now, only add if normalised - todo
			rawMsg msg = new rawMsg();
			try {
				msg.v[0] = Float.valueOf(values.get(0).toString()).floatValue();
				msg.v[1] = Float.valueOf(values.get(1).toString()).floatValue();
				msg.v[2] = Float.valueOf(values.get(2).toString()).floatValue();
				msg.v[3] = Float.valueOf(values.get(3).toString()).floatValue();
				msg.v[4] = Float.valueOf(values.get(4).toString()).floatValue();
				msg.v[5] = Float.valueOf(values.get(5).toString()).floatValue();

			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			this.lock.lock();
			PlatformMiddleware.msgQueue.add(msg);
			this.lock.unlock();
		}
		else
		{
		   // todo - scale non normalized values	
		}
	}

	void parseXyzrpy(boolean isNormalized, JSONArray values) {
		// System.out.print(" parseXyzrpy "); System.out.println( values);
		if (isNormalized) { // for now, only add if normalised - todo
			xyzMsg msg = new xyzMsg();
			// System.out.println(values);
			// System.out.println(values.toString());
			try {
				msg.setX(Float.valueOf(values.get(0).toString()).floatValue());
				msg.setY(Float.valueOf(values.get(1).toString()).floatValue());
				msg.setZ( Float.valueOf(values.get(2).toString()).floatValue());
				msg.setRoll(Float.valueOf(values.get(3).toString()).floatValue());
				msg.setPitch(Float.valueOf(values.get(4).toString()).floatValue());
				msg.setYaw(Float.valueOf(values.get(5).toString()).floatValue());

			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			this.lock.lock();
			PlatformMiddleware.msgQueue.add(msg);
			this.lock.unlock();
		}
		else
		{
		   // todo - scale non normalized values	
		}
	}

	void parseConfig(JSONObject json1) {
		 System.out.println(values.toString());

		cfg.gainX = getOptionalField(json1, "gainX", cfg.gainX);
		cfg.gainY = getOptionalField(json1, "gainY", cfg.gainY);
		cfg.gainZ = getOptionalField(json1, "gainZ", cfg.gainZ);
		cfg.gainRoll = getOptionalField(json1, "gainRoll", cfg.gainRoll);
		cfg.gainPitch = getOptionalField(json1, "gainPitch", cfg.gainPitch);
		cfg.gainYaw = getOptionalField(json1, "gainYaw", cfg.gainYaw);
		cfg.gain = getOptionalField(json1, "gain", cfg.gain);

		cfg.washoutX = getOptionalField(json1, "washoutX", cfg.washoutX);
		cfg.washoutY = getOptionalField(json1, "washoutY", cfg.washoutY);
		cfg.washoutZ = getOptionalField(json1, "washoutZ", cfg.washoutZ);
		cfg.washoutRoll = getOptionalField(json1, "washoutRoll", cfg.washoutRoll);
		cfg.washoutPitch = getOptionalField(json1, "washoutPitch", cfg.washoutPitch);
		cfg.washoutYaw = getOptionalField(json1, "washoutYaw", cfg.washoutYaw);
	}

	void printConfig()	{
		  System.out.print("gainX="); System.out.println(cfg.gainX);		  
		  System.out.print("gainY="); System.out.println(cfg.gainY); 
		  System.out.print("gainZ="); System.out.println(cfg.gainZ); 
		  System.out.print("gainRoll="); System.out.println(cfg.gainRoll); 
		  System.out.print("gainPitch="); System.out.println(cfg.gainPitch); 
	      System.out.print("gainYaw="); System.out.println(cfg.gainYaw); 
		  System.out.print("gain="); System.out.println(cfg.gain);
		  
		  System.out.print("washoutX="); System.out.println(cfg.washoutX);
		  System.out.print("washoutY="); System.out.println(cfg.washoutY);
		  System.out.print("washoutZ="); System.out.println(cfg.washoutZ);
		  System.out.print("washoutRoll="); System.out.println(cfg.washoutRoll);
		  System.out.print("washoutPitch="); System.out.println(cfg.washoutPitch);
		  System.out.print("washoutYaw="); System.out.println(cfg.washoutYaw);		
	}

	void parseMsg(String msg) {
		// todo - needs robust error handling for missing keys and values
		JSONParser parser = new JSONParser();
		try {
			Object obj = parser.parse(msg);
			JSONObject jsonObject = (JSONObject) obj;

			if ((boolean) (jsonObject.get("method").equals("config"))) {
				parseConfig(jsonObject);
				printConfig();
			} else // its a movement message?, parse fields
			{
				// print(json1);
				boolean isNormalized = true;
				if(jsonObject.containsKey("units")) {
				    if ((boolean) (jsonObject.get("units").equals("real")))
					    isNormalized = false;
				    else if ((boolean) (jsonObject.get("units").equals("norm")))
					    isNormalized = true; // default, but set anyway	
				}
				JSONArray values = (JSONArray) jsonObject.get("args");
				if ((boolean) (jsonObject.get("method").equals("raw")))
					parseRaw(isNormalized, values);
				else if ((boolean) (jsonObject.get("method").equals("xyzrpy")))
					parseXyzrpy(isNormalized, values);
			}
		} catch (ParseException e) {
			e.printStackTrace();
		}
	}

	public void run() {		
		try {	
			// open server connection for client
			middlewareServer = new ServerSocket(MIDDLEWARE_PORT);		
			Socket client = middlewareServer.accept();
			System.out.print("Connected to " + client.getRemoteSocketAddress().toString());
			BufferedReader inFromClient = new BufferedReader(new InputStreamReader(client.getInputStream()));
			String msg;			
			while (true) {
				try {
					if ((msg = inFromClient.readLine()) != null) {
						// System.out.println(msg);
						if(System.currentTimeMillis() - prevMsgTime > INACTIVITY_TIMEOUT) {
							resetShaping();
							System.out.println("inactivity timemout on socket readLine");
						}
						prevMsgTime = System.currentTimeMillis();
						parseMsg(msg);
					}
					else {						
						System.out.println("Client Disconnected, waiting for new connection");
						client = middlewareServer.accept();
						System.out.print("Connected to " + client.getRemoteSocketAddress().toString());
						inFromClient = new BufferedReader(new InputStreamReader(client.getInputStream()));
					}
				} catch (Exception e) {
					e.printStackTrace();
					break;
				}
			}
		} catch (IOException e) {
			System.err.println(e);
		}
	}
}
