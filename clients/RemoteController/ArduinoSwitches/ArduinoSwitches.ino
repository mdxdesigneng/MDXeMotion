void setup() {
  Serial.begin(9600):
  for(int i=10; i < 13; i++) {
    pinMode(i, INPUT_PULLUP);
  }
}

void loop() {
   if(digitalRead(10) == LOW {
       send("dispatch");
       waitRelease(10);
   }
   else if(digitalRead(11) == LOW {
       send("pause")
       waitRelease(11);
   }
   if(digitalRead(12) == LOW {
       send("reset")
       waitRelease(12);
}

void send( char *msg) {
   Serial.println(msg);
}


void waitRelease( int pin) {
  delay(20); // crude debounce
  while(digitalRead(pin) == LOW )
     ;
}

