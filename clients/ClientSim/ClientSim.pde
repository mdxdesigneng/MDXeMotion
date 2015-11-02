//  generates client messages to middleware
import peasy.*;
import controlP5.*;
import processing.net.*;
 
import processing.serial.*;

float MAX_TRANSLATION = 30;
float MAX_ROTATION = PI/6;
float scale = .5;

ControlP5 cp5;
PeasyCam camera;
Platform mPlatform;
//ParseMessage parser;

private static final int mwPort =  10002;
private static final String  MiddlewareIp = "localhost";
Client mwClient;

private static final int chairPort =  10003;
private static final String  chairIp = "localhost";
Client chairClient;

float posX=0, posY=0, posZ=0, rotX=0, rotY=0, rotZ=0;

CheckBox chkSend;
CheckBox chkChair;  // sends to middleware when unchecked, to chair when checked

PrintWriter output; // for csv output
boolean isClientActive = false;

int BLACK = 0x0; 

void setup()
{
  frameRate(10);  // messages per second
  size(768, 500, P3D);
  background(0);
  fill(255);
   
  mwClient = new Client(this, MiddlewareIp, mwPort);
  chairClient = new Client(this, chairIp, chairPort);
   
  smooth();
  textSize(16);

  camera = new PeasyCam(this, 666);
  camera.setPitchRotationMode();
  camera.setRotations(-1.0, 0.0, 0.0);
  camera.lookAt(8.0, -50.0, 250.0);
  
  mPlatform = new Platform(scale);
  mPlatform.applyTranslationAndRotation(new PVector(), new PVector());
  
  cp5 = new ControlP5(this);

 cp5.addSlider("posX")
    .setPosition(20, 20)
      .setSize(180, 40).setRange(-1, 1)
       .setColorCaptionLabel(BLACK);
  cp5.addSlider("posY")
    .setPosition(20, 70)
      .setSize(180, 40).setRange(-1, 1)
        .setColorCaptionLabel(BLACK);
  cp5.addSlider("posZ")
    .setPosition(20, 120)
      .setSize(180, 40).setRange(-1, 1)
        .setColorCaptionLabel(BLACK);

  cp5.addSlider("rotX")
    .setPosition(width-210, 20)
      .setSize(180, 40).setRange(-1, 1)
        .setColorCaptionLabel(BLACK);
  cp5.addSlider("rotY")
    .setPosition(width-210, 70)
      .setSize(180, 40).setRange(-1, 1)
        .setColorCaptionLabel(BLACK);
  cp5.addSlider("rotZ")
    .setPosition(width-210, 120)
      .setSize(180, 40).setRange(-1, 1)
        .setColorCaptionLabel(BLACK);

  chkSend = cp5.addCheckBox("send")
    .setPosition(100, 200)
      .setSize(40, 40)
        .setItemsPerRow(1)   
          .setColorActive(color(255,0,0))
           .setColorLabel(BLACK)    
             .addItem("Send", 0)  ;
          
  chkChair = cp5.addCheckBox("chair")
    .setPosition(100, 250)
      .setSize(40, 40)
        .setItemsPerRow(1)   
          .setColorActive(color(255,0,0)) 
            .setColorLabel(BLACK)   
              .addItem("Chair", 0) ;          

  cp5.setAutoDraw(false);
  camera.setActive(true); 
  
 
  String s = "{\"jsonrpc\":\"2.0\",\"method\":\"config\",\"ClientName\":\"ClientSim\"}\n";                                       
  mwClient.write(s) ;  
}


void draw() { 
  background(225);
  
  mPlatform.applyTranslationAndRotation(PVector.mult(new PVector(posX, posY, posZ), MAX_TRANSLATION), 
                     PVector.mult(new PVector(rotY, rotX, rotZ), MAX_ROTATION));                     
  if ( chkSend.getState(0) == true) {
      if ( chkChair.getState(0) == true) {
        // send to chair
         String s = String.format("{\"jsonrpc\":\"2.0\",\"method\":\"moveEvent\",\"xyzArgs\":[%f,%f,%f, %f,%f,%f]}\n",
                        posX, posY, posZ,rotX, rotY, rotZ);                      
          chairClient.write(s) ;
          isClientActive = true;      
          println(s);
       }   
       else if (mwClient !=null && mwClient.active()) {
          // send to middleware
            String s = String.format("{\"jsonrpc\":\"2.0\",\"method\":\"xyzrpy\",\"args\":[%f,%f,%f, %f,%f,%f]}\n",
                          posX, posY, posZ,rotX, rotY, rotZ);                      
            mwClient.write(s) ;
            print(s);
            isClientActive = true;      
            println(s);
         }
     } 
     else {
       isClientActive = false;      
     }     
 

  mPlatform.draw();
  hint(DISABLE_DEPTH_TEST);
  camera.beginHUD();
  fill(100);
  text("Press space to reset translations and rotations to 0",20,470); 
  if(chkSend.getState(0) && isClientActive == false) {
       fill(0);
       text("Not connected",20,340); 
  }
  cp5.draw();
  camera.endHUD();
  hint(ENABLE_DEPTH_TEST);
}


void stop() {
  
} 


void controlEvent(ControlEvent theEvent) {
  camera.setActive(false);
  /*  
   //after a UI event send a message?
   */
}

void mouseReleased() {
  camera.setActive(true);
}

void keyPressed() {
  if (key == ' ') {
    camera.setRotations(-1.0, 0.0, 0.0);
    camera.lookAt(8.0, -50.0, 250.0);
    camera.setDistance(666);
        
    cp5.getController("posX").setValue(0);  
    cp5.getController("posY").setValue(0);
    cp5.getController("posZ").setValue(0);
    cp5.getController("rotX").setValue(0);  
    cp5.getController("rotY").setValue(0);
    cp5.getController("rotZ").setValue(0);    
    posX = posY = posZ = rotX = rotY = rotZ = 0;
  }
}
