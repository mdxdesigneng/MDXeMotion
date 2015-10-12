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

UDP udp;  // the UDP object

float posX=0, posY=0, posZ=0, rotX=0, rotY=0, rotZ=0;

CheckBox chkSliders;
CheckBox chkInvert;
Button  btnDef;

PrintWriter output; // for csv output
boolean isCoaseterRunning = false;

boolean isChair;  // flag indicating chair or servo platform
boolean echoToSerial = false;
boolean dumpCSV = false;

void setup()
{
  size(1024, 600, P3D);
  background(0);

  if (echoToSerial) {  
    println(Serial.list());
    println(" Connecting to -> " + Serial.list()[portIndex]);
    myPort = new Serial(this, Serial.list()[portIndex], 57600);
  }
  if (dumpCSV) {
    output = createWriter("capture.csv");  // for csv output
  }
  
  // create a multicast connection on multicastPort
  // and join the group at multicastIP address
  udp = new UDP( this, multicastPort, multicastIP );
  // wait constantly for incomming data
  udp.listen( true );

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

  chkSliders = cp5.addCheckBox("UseSliders")
    .setPosition(100, 200)
      .setSize(40, 40)
        .setItemsPerRow(1)       
          .addItem("Use Sliders", 0)  ;

  chkInvert = cp5.addCheckBox("invert")
    .setPosition(width-210, 220)
      .setSize(40, 40)
        .setItemsPerRow(1)       
          .addItem("Invert", 0)  ;

  btnDef = cp5.addButton("Change_Platform")
    .setValue(128)
      .setPosition(width-210, 190)
        .setSize(80, 25)
          .setCaptionLabel("Change Platform") 
            .updateSize()
              ;    


  cp5.setAutoDraw(false);
  camera.setActive(true);
}

/**
 * This is the program receive handler. To perform any action on datagram 
 * reception, you need to implement this method in your code. She will be 
 * automatically called by the UDP object each time he receive a nonnull 
 * message.
 */
void receive( byte[] data ) {
    String msg=null;
   try { 
       msg = new String(data, "UTF-8"); 
    } catch (UnsupportedEncodingException e) {
      e.printStackTrace();
    }
    
    if (msg != null) {     
      int index =  msg.indexOf("{");
      if ( index >=0) {
         msg = msg.substring(index);       
         println(msg);
        if( parser.isGeometryRequest(msg) ){          
             ; // todo );            
        } else {              
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
}

void draw() { 
  background(200); 
  

  if ( chkSliders.getState(0) == true) {
    // use slider if set
    mPlatform.applyTranslationAndRotation(PVector.mult(new PVector(posX, posY, posZ), MAX_TRANSLATION), 
    PVector.mult(new PVector(rotY, rotX, rotZ), MAX_ROTATION));
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

