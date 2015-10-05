

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;

public class ChairInterface {
	private final String CHAIR_IP   = "localhost";
	private final int CHAIR_PORT = 10003;
	
	Socket chairClient;
	DataOutputStream toChair;
	DataInputStream  fromChair; // not used in this version
	
	
	public boolean begin() {  // returns false if unable to connect to the chair socket
		try {
			   chairClient = new Socket(CHAIR_IP, CHAIR_PORT);
		       toChair = new DataOutputStream(chairClient.getOutputStream());
		       fromChair = new DataInputStream( chairClient.getInputStream()); 
		       System.out.println("Connected to Chair socket");	
		       return true;
		    }
		    catch (IOException e) {
		       System.out.print(e);
		       System.out.println("\n Unable to connect to Chair, ensure Chair Server is running and available");		   
	        } 
		    return false; 
	}
	
	public void end() {
		 try {
			  if( chairClient != null)
			      chairClient.close();
	    	} catch (IOException e) {		
			   e.printStackTrace();
		    }
	}
	
	public float map(float value, float inMin, float inMax, float outMin, float outMax) {
	    return outMin + (outMax - outMin) * ((value - inMin) / (inMax - inMin));
    }
	
	public void sendXyzrpy( PlatformApi.xyzMsg msg){
		   String s = String.format("{\"jsonrpc\":\"2.0\",\"method\":\"xyzrpy\",\"args\":[%f,%f,%f, %f,%f,%f]}\n",
                   msg.getX(), msg.getY(), msg.getZ(), msg.getRoll(),msg.getPitch(), msg.getYaw());
           System.out.print(s);	
           try {
              toChair.writeUTF(s);
           }
           catch (IOException e) {   			
   			//e.printStackTrace();
   			System.out.print("error writing to chair, trying to reconnect");
   			this.end();
   			this.begin();   			
   		}
	}
	
	public void sendRaw( PlatformApi.msgFields msg){
		   String s = String.format("{\"jsonrpc\":\"2.0\",\"method\":\"raw\",\"args\":[%f,%f,%f, %f,%f,%f]}\n",
                msg.v[0], msg.v[1], msg.v[2], msg.v[3], msg.v[4], msg.v[5]);
        System.out.print(s);	
        try {
           toChair.writeUTF(s);
        }
        catch (IOException e) {   			
			//e.printStackTrace();
			System.out.print("error writing to chair, trying to reconnect");
			this.end();
			this.begin();   			
		}
	}

}
