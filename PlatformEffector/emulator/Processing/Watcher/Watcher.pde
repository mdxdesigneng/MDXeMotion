import peasy.*;
import controlP5.*;
import processing.net.*;

import java.io.UnsupportedEncodingException;
import processing.serial.*;
import hypermedia.net.*;    // import UDP library
Serial myPort;               // Create object from Serial class
public static final short portIndex = 0;  // select the com port

float MAX_TRANSLATION = 30;
float MAX_ROTATION = PI/6;


ControlP5 cp5;
PeasyCam camera;
Platform mPlatform;
ParseMessage parser;

private static final int multicastPort =  10005;
private static final String multicastIP =  "239.255.0.5";


Client thisClient; 

CheckBox chkInvert;
Button  btnDef;

PrintWriter output; // for csv output
boolean isCoaseterRunning = false;

boolean isChair;  // flag indicating chair or servo platform
boolean echoToSerial = false;
boolean dumpCSV = false;

private static final String  MiddlewareIp = "localhost";
private static final int watcherPort =  10004;

void setup()
{
  size(700, 600, P3D);
  background(0);

  if (echoToSerial) {  
    println(Serial.list());
    println(" Connecting to -> " + Serial.list()[portIndex]);
    myPort = new Serial(this, Serial.list()[portIndex], 57600);
  }
  if (dumpCSV) {
    output = createWriter("capture.csv");  // for csv output
  }

  thisClient = new Client(this, MiddlewareIp, watcherPort);
  parser = new ParseMessage();

  smooth();
  textSize(20);

  camera = new PeasyCam(this, 666);
  camera.setPitchRotationMode();
  camera.setRotations(-1.0, 0.0, 0.0);
  camera.lookAt(8.0, -50.0, 80.0);

  mPlatform = new Platform(ServoPlatformDef);
  mPlatform.applyTranslationAndRotation(new PVector(), new PVector());

  cp5 = new ControlP5(this);
  
 chkInvert = cp5.addCheckBox("invert")
    .setPosition(width-100, height - 80)
      .setSize(40, 40)
        .setItemsPerRow(1)    
          .setColorLabel(0)      
            .addItem("Invert", 0)  ;

  btnDef = cp5.addButton("Change_Platform")
    .setValue(128)
      .setPosition(width-100, height-30)
        .setSize(80, 25)
          .setCaptionLabel("Change Platform") 
            .updateSize()
              ;    


  cp5.setAutoDraw(false);
  camera.setActive(true);
}


void draw() { 
  background(240); 
  
  if (thisClient !=null) {       
    String msg = thisClient.readStringUntil('\n'); 
     if (msg != null) {     
      int index =  msg.indexOf("{");
      if ( index >=0) {
         msg = msg.substring(index);       
         println(msg);                  
          msgFields m = parser.parseMsg(msg);
          if ( m != null) {
            if ( chkInvert.getState(0) == true) { 
              mPlatform.applyTranslationAndRotation(PVector.mult(new PVector(m.x, m.y, m.z), MAX_TRANSLATION), 
              PVector.mult(new PVector(m.pitch, m.roll, m.yaw), MAX_ROTATION));
              println("check invert");
            } else {
              mPlatform.applyTranslationAndRotation(PVector.mult(new PVector(m.x, m.y, m.z), MAX_TRANSLATION), 
              PVector.mult(new PVector(-m.pitch, m.roll, m.yaw), MAX_ROTATION));
            }

            String outMsg = String.format("xyzrpy,%f,%f,%f,%f,%f,%f\n", m.x, m.y, m.z, m.roll, m.pitch, m.yaw);
            print(outMsg);
            if (echoToSerial) {
              myPort.write(outMsg);
            }
          }
       }
     } 
  }    
  
  mPlatform.draw();

  hint(DISABLE_DEPTH_TEST);
  camera.beginHUD();
  fill(0);
  for (int i=0; i < 6; i++) {
    text(String.format("%.1f", mPlatform.l[i].mag() / mPlatform.scale), 20, 400 + (30*i)); // show lengths
  }


  cp5.draw();
  camera.endHUD();
  hint(ENABLE_DEPTH_TEST);
}


// function receive changes from controller with same name 
public void Change_Platform(int theValue) { 
  isChair = !isChair; 
  if (isChair)
    mPlatform = new Platform(ChairPlatformDef);
  else  
    mPlatform = new Platform(ServoPlatformDef);

  mPlatform.applyTranslationAndRotation(new PVector(0, 0, 0), new PVector(0, 0, 0) );  // redraw
}

void mouseReleased() {
  camera.setActive(true);
}

void keyPressed() {
  if (key == ' ') {
    camera.setRotations(-1.0, 0.0, 0.0);
    camera.lookAt(8.0, -50.0, 80.0);
    camera.setDistance(666);
  }
}

