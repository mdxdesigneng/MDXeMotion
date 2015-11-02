
import processing.net.*;

float MAX_TRANSLATION = 30;
float MAX_ROTATION = PI/6;

Platform mPlatform;
ParseMessage parser;

private static final int thisPort =  10003;
Server myServer;

boolean isConnected = false;


void setup()
{
  size(600, 400);
  background(200);
  fill(0);  
  textSize(20);  
  
  myServer = new Server(this, thisPort);
  parser = new ParseMessage();
  
  mPlatform = new Platform(ChairPlatformDef);
  mPlatform.applyTranslationAndRotation(new PVector(), new PVector());

}

void draw() { 
    background(200);
  // Get the next available client 
  Client thisClient = myServer.available(); 
  if (thisClient !=null) {       
    String msg = thisClient.readStringUntil('\n');       
    if (msg != null) {     
      int index =  msg.indexOf("{");
      if ( index >=0) {
         msg = msg.substring(index);       
        // println(msg);
        if( parser.isGeometryRequest(msg) ){          
            geometryReply(thisClient);            
        } else {              
          float vals[] = parser.parseMsg(msg);
          if ( vals != null) {
            
            for (int i=0; i < 6; i++) {
                text(String.format("%.1f", vals[i]), 20, 40 + (30*i)); // show lengths 
            }
    
          }
        }
      }
    }
  }
 
  if (isConnected ) {        
    text("Connected", width-210, height-40);
  } else {
    text("Not Connected to Middleware", width-300, height-40);
  } 
}

void geometryReply(Client c) {
  JSONObject j = new JSONObject(); 
  j.setString("jsonrpc","2.0");
  j.setString("reply","geometry");
  j.setString("effectorName","PlatformSimulator");    
  j.setFloat("baseRadius", mPlatform.baseRadius);
  JSONArray baseArray = new JSONArray();
  for (int i = 0; i < 6; i++) {   
    baseArray.setFloat(i, ChairPlatformDef.baseAngles[i]);    
  }  
  j.setJSONArray("baseAngles", baseArray);
  j.setFloat("platformRadius", mPlatform.platformRadius);
  JSONArray platformArray = new JSONArray();
  for (int i = 0; i < 6; i++) {   
    platformArray.setFloat(i, ChairPlatformDef.platformAngles[i]);    
  }  
  j.setJSONArray("platformAngles", platformArray);
 
 
  JSONArray actuatorLen = new JSONArray();
  actuatorLen.setFloat(0, ChairPlatformDef.minActuatorLen);    
  actuatorLen.setFloat(1, ChairPlatformDef.maxActuatorLen);  
  j.setJSONArray("actuatorLen", actuatorLen);
  
 // j.setFloat("actuatorLen", mPlatform.actuatorLen);
  j.setFloat("initialHeight", ChairPlatformDef.initialHeight); // todo !!!
  j.setFloat("maxTranslation", ChairPlatformDef.maxTranslation);
  j.setFloat("maxRotation", ChairPlatformDef.maxRotation);

  String s = j.format(-1);                
  c.write(s + "\n") ; 
  println(s);
} 

void serverEvent(Server someServer, Client c) {
  println("We have a new client: " + c.ip());
  isConnected = true;
}

void disconnectEvent(Client c) {  
  println("Client side: a client disconnected: " + c);
  isConnected = false;
}



