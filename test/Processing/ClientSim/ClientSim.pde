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

private static final int thisPort =  10002;
private static final String  MiddlewareIp = "localhost";
Client myClient;

float posX=0, posY=0, posZ=0, rotX=0, rotY=0, rotZ=0;

CheckBox checkbox;

PrintWriter output; // for csv output
boolean isClientActive = false;


void setup()
{
  frameRate(10);  // messages per second
  size(768, 500, P3D);
  background(0);
  fill(255);
   
  myClient = new Client(this, MiddlewareIp, thisPort);
   
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
      .setSize(180, 40).setRange(-1, 1);
  cp5.addSlider("posY")
    .setPosition(20, 70)
      .setSize(180, 40).setRange(-1, 1);
  cp5.addSlider("posZ")
    .setPosition(20, 120)
      .setSize(180, 40).setRange(-1, 1);

  cp5.addSlider("rotX")
    .setPosition(width-210, 20)
      .setSize(180, 40).setRange(-1, 1);
  cp5.addSlider("rotY")
    .setPosition(width-210, 70)
      .setSize(180, 40).setRange(-1, 1);
  cp5.addSlider("rotZ")
    .setPosition(width-210, 120)
      .setSize(180, 40).setRange(-1, 1);

  checkbox = cp5.addCheckBox("send")
    .setPosition(100, 200)
      .setSize(40, 40)
        .setItemsPerRow(1)   
          .setColorActive(color(255,0,0))    
          .addItem("Send", 0)  ;

  cp5.setAutoDraw(false);
  camera.setActive(true); 
}


void draw() { 
  background(200);
  
  mPlatform.applyTranslationAndRotation(PVector.mult(new PVector(posX, posY, posZ), MAX_TRANSLATION), 
                     PVector.mult(new PVector(rotY, rotX, rotZ), MAX_ROTATION));                     
  if ( checkbox.getState(0) == true) {    
    if (myClient !=null && myClient.active()) {
        String s = String.format("{\"jsonrpc\":\"2.0\",\"method\":\"xyzrpy\",\"args\":[%f,%f,%f, %f,%f,%f]}\n",
                      posX, posY, posZ,rotX, rotY, rotZ);                      
        myClient.write(s) ;
        isClientActive = true;      
        println(s);
     } 
     else {
       isClientActive = false;
     }  
  }

  mPlatform.draw();
  hint(DISABLE_DEPTH_TEST);
  camera.beginHUD();
  fill(100);
  text("Press space to reset translations and rotations to 0",20,470); 
  if(checkbox.getState(0) && isClientActive == false) {
       fill(0);
       text("Client not connected",20,300); 
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
