/* 
 * ArduinoSwitches.ino 
 * sends switch presses to RemoteControl.py
   switches connected to pins 9 through 12
 * displays received state info
 * States are: ready, running, paused, emergency stop
 * LED indicators connecteed to pins 4 through 7
 */

#include <Bounce.h>

const byte debounceT = 10; // max bounce duration in milliseconds

 int firstOutPin = 4; // indicators connected to pins starting from here
 int nbrOutpins = 4; // number of indicators

 Bounce stopBtn     = Bounce( 9, debounceT); 
 Bounce dispatchBtn = Bounce(10, debounceT);  
 Bounce pauseBtn    = Bounce(11, debounceT);  
 Bounce resetBtn    = Bounce(12, debounceT); 
  
void setup() {
  Serial.begin(57600);
  for(int i = 0; i <nbrOutpins; i++ ) {
      pinMode(i+firstOutPin, OUTPUT); 
  }
  for(int i=9; i < 13; i++) {
    pinMode(i, INPUT_PULLUP);
  }
  pinMode(13, OUTPUT); // onboard LED indicates activity (only needed for debug)
}

void loop() {       
  if(stopBtn.update() && stopBtn.fallingEdge()) {
       send("emergencyStop");      
   }
   else if(dispatchBtn.update() && dispatchBtn.fallingEdge()) {
       send("dispatch");      
   }
   else if(pauseBtn.update() && pauseBtn.fallingEdge()) {
       send("pause");      
   }
   else if(resetBtn.update() && resetBtn.fallingEdge()) {
       send("reset");      
   }
   if(Serial.available()) {
      digitalWrite(13, HIGH);  // faint light on LED if receiving status updates
      byte c = Serial.read() - '0';
      digitalWrite(13, LOW);
      for(int i = 0; i <nbrOutpins; i++ ) {
          digitalWrite(i+firstOutPin, i == c);     
      }      
   }    
}

void send( char *msg) {
   digitalWrite(13, HIGH);
   Serial.println(msg);
   delay(10);  // short delay to flash LED showing button press has been sent
   digitalWrite(13, LOW);
}


