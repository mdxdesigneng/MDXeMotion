// this code handles connection to the primary effector (chair) server
// secondary watchers can connect as clients

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ConnectException;
import java.net.InetAddress;
import java.net.Socket;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class EffectorInterface {
    private InetAddress effectorIP;
    private int effectorPort;
    // This is the TCP server that advertises everything that is sent
    // to the chair (see AnnouncementServer.java)
    AnnouncementServer announcer = null;
    
    
    Socket effectorClient = null;
    DataOutputStream toEffector=null;;  
    
    public static class effectorDef {
        String name;              // the name identifying this effector  
        float baseAngles[] ;
        float baseRadius;         // mm     
        float platformAngles[] ;
        float platformRadius;     // mm
        float actuatorLen[];      // min, max millimetres
        float initialHeight;      // mm distance between the base and platform when centered
        float maxTranslation;     // mm
        float maxRotation;        // angle in degrees
        float minActuatorLen;     // mm 
        float maxActuatorLen;     // mm 
        public effectorDef() {
            baseAngles = new float[6];
            platformAngles = new float[6];
            actuatorLen = new float[2];                 
        }
    }   

    effectorDef effectorGeometry;   
    
    public effectorDef begin(InetAddress ip, int port, int watcherPort ) {  // returns false if unable to connect to the Effector socket
       effectorIP = ip;
       effectorPort = port;   
       if( connectToEffector()) {   
          announcer = new AnnouncementServer(watcherPort);
          announcer.start();        
          return effectorGeometry;
       }
       return null;
    }
    
    public effectorDef getGeometry() {      
        return effectorGeometry;
    }   

    private boolean connectToEffector(){
        try {
           effectorClient = new Socket(effectorIP, effectorPort);
           toEffector = new DataOutputStream(effectorClient.getOutputStream());      
           System.out.println("Middleware connected to Effector socket");   
           effectorGeometry = new effectorDef();
           if(requestGeometry())
              return true;
        }          
        catch (IOException e) {
           System.out.print(e);
           System.out.println("\n Unable to connect to Effector, ensure Effector Server is running and available on " +  effectorIP.getHostAddress());         
        } 
        return false;
    
    }
    
    
    public void end() {
         try {
              if( effectorClient != null)
                  effectorClient.close();
            } catch (IOException e) {       
               e.printStackTrace();
            }
    }
    
    public float map(float value, float inMin, float inMax, float outMin, float outMax) {
        return outMin + (outMax - outMin) * ((value - inMin) / (inMax - inMin));
    }
    
    void showGeometry() {
         System.out.print("name: "); System.out.println(effectorGeometry.name); 
          System.out.print("baseRadius="); System.out.println(effectorGeometry.baseRadius);      
          float[] b = effectorGeometry.baseAngles.clone();
          System.out.println(String.format("baseAngles=[%f,%f,%f, %f,%f,%f]",b[0],b[1],b[2],b[3],b[4],b[5]));
          System.out.print("platformRadius="); System.out.println(effectorGeometry.platformRadius);     
          float[] p = effectorGeometry.platformAngles.clone();
          System.out.println(String.format("platformAngles=[%f,%f,%f, %f,%f,%f]",p[0],p[1],p[2],p[3],p[4],p[5]));
          System.out.print("initialHeight="); System.out.println(effectorGeometry.initialHeight);
          System.out.print("maxTranslation="); System.out.println(effectorGeometry.maxTranslation);
          System.out.print("maxRotation="); System.out.println(effectorGeometry.maxRotation);
          System.out.print("minActuatorLen="); System.out.println(effectorGeometry.minActuatorLen);
          System.out.print("maxActuatorLen="); System.out.println(effectorGeometry.maxActuatorLen);
    
    }

    void parseGeometry(String msg) {
        JSONParser parser = new JSONParser();
        try {
            Object obj = parser.parse(msg);
            JSONObject jsonObject = (JSONObject) obj;

            if ((boolean) (jsonObject.get("reply").equals("geometry"))) {
                // todo - this needs code to handle missing or malformed messages !!!
                effectorGeometry.name =  jsonObject.get("effectorName").toString();
                effectorGeometry.platformRadius = Float.valueOf(jsonObject.get("platformRadius").toString()).floatValue();
                effectorGeometry.baseRadius = Float.valueOf(jsonObject.get("baseRadius").toString()).floatValue();              
                JSONArray platformAngles = (JSONArray) jsonObject.get("platformAngles");
                JSONArray baseAngles = (JSONArray) jsonObject.get("baseAngles");                
                for(int i=0; i < 6; i++){
                    effectorGeometry.platformAngles[i] = Float.valueOf(platformAngles.get(i).toString()).floatValue();
                    effectorGeometry.baseAngles[i] = Float.valueOf(baseAngles.get(i).toString()).floatValue();
                }               
                JSONArray actuatorLen = (JSONArray) jsonObject.get("actuatorLen");
                effectorGeometry.minActuatorLen = Float.valueOf(actuatorLen.get(0).toString()).floatValue();
                effectorGeometry.maxActuatorLen = Float.valueOf(actuatorLen.get(1).toString()).floatValue();
                effectorGeometry.initialHeight = Float.valueOf(jsonObject.get("initialHeight").toString()).floatValue();
                effectorGeometry.maxTranslation = Float.valueOf(jsonObject.get("maxTranslation").toString()).floatValue();
                effectorGeometry.maxRotation = Float.valueOf(jsonObject.get("maxRotation").toString()).floatValue();
            
            } 
            else {// its not the reply we want
                System.out.print("reply does not contain well formed geometry message");    
            }
        } catch (ParseException e) {
            e.printStackTrace();        
        }
    }

    
    private  boolean requestGeometry() {
        try {           
            toEffector.writeUTF("{\"jsonrpc\":\"2.0\",\"method\":\"geometry\"}\n");
        
            effectorClient.setSoTimeout(5000);  // wait up to 5 seconds for a reply             
            BufferedReader input =      
               new BufferedReader(new InputStreamReader(effectorClient.getInputStream()));
            String reply =  (String) input.readLine();          
            if(reply != null){
                parseGeometry(reply);   
                showGeometry(); 
            }
            else {
                System.out.println("timout waiting for a reply to get geometry message");       
            }           
            
        } catch (ConnectException e) {
              System.out.println("error requesting geometry from Effector, trying to reconnect ");
              this.end();
              connectToEffector(); 
             }
        catch (IOException e) {         
             System.out.println("error requesting geometry from Effector:" + e.toString() );    
        }
        return true;
    }
    
    public void sendMoveEvent(float [] raw, float[] xyz){
         boolean isWriteSuccessful = false; 
         String s = "{\"jsonrpc\":\"2.0\",\"method\":\"moveEvent\",";        
          //  send raw values as floats and extents as ints
          s = s + String.format("\"rawArgs\":[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f],\"xyzArgs\":[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f],\"extents\":[%.0f,%.0f,%.0f,%.0f]}\n",
                 raw[0], raw[1], raw[2], raw[3], raw[4], raw[5], xyz[0], xyz[1], xyz[2], xyz[3], xyz[4], xyz[5],
                 effectorGeometry.maxTranslation, effectorGeometry.maxRotation,  effectorGeometry.actuatorLen[0], effectorGeometry.actuatorLen[1]  );
         
         //System.out.print(s); 
         try {
            toEffector.writeUTF(s);
            isWriteSuccessful = true;
         }
         catch (ConnectException e) {
            System.out.print("Effector connection error, trying to reconnect");
    
         }
         catch (IOException e) {            
            System.out.print("error writing moveEvent to Effector, trying to reconnect");
            System.out.println(e);
                
        }
        announcer.announce(s); // Send to announce clients
        if(! isWriteSuccessful) {
            this.end();
            connectToEffector();
        }
          
        
    }
    
    public void activateEffector(boolean activate) {
        System.out.println("Activating:" + activate );
        try {
            if( activate ){
               toEffector.writeUTF("{\"jsonrpc\":\"2.0\",\"method\":\"activate\"}\n");
            }
            else {
                toEffector.writeUTF("{\"jsonrpc\":\"2.0\",\"method\":\"deactivate\"}\n");
            }
            
        } catch (ConnectException e) {
              System.out.println("error connecting when trying to set activation");          
             }
        catch (IOException e) {         
             System.out.println("error setting effector activation:" + e.toString() );  
        }
    }

}
