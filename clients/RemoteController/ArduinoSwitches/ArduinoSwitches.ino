 int firstOutPin = 6; // indicators connected to pins starting from here
 int nbrOutpins = 3; // number of indicators

void setup() {
  Serial.begin(9600);
  for(int i = 0; i <nbrOutpins; i++ ) {
      pinMode(i+firstOutPin, OUTPUT); 
  }
  for(int i=9; i < 13; i++) {
    pinMode(i, INPUT_PULLUP);
  }
}

void loop() {       
  if(digitalRead(9) == LOW) {
       send("emergencyStop");
       waitRelease(10);
   }
   if(digitalRead(10) == LOW) {
       send("dispatch");
       waitRelease(10);
   }
   else if(digitalRead(11) == LOW) {
       send("pause");
       waitRelease(11);
   }
   if(digitalRead(12) == LOW) {
       send("reset");
       waitRelease(12);
   }
   if(Serial.available()) {
      byte c = Serial.read();
      for(int i = 0; i <nbrOutpins; i++ ) {
        digitalWrite(i+firstOutPin, bitRead(c, i)); 
      }      
   }    
}

void send( char *msg) {
   Serial.println(msg);
}

void waitRelease( int pin) {
  delay(20); // crude debounce
  while(digitalRead(pin) == LOW )
     ;
}

