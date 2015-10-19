/* Arduino Controlled Rotary Stewart Platform
   Responds to simplified raw  middleware messsages
   Todo (code is still xyz)
*/

#include <Servo.h>
#include <Wire.h>
#include "printf.h"

#define MAX 160 // servo angles
#define MIN 20

//Positions of servos mounted in opposite direction
#define INV1 1
#define INV2 3
#define INV3 5

//constants for computation of positions of connection points
#define deg2rad 180/PI
#define deg30 PI/6

float rawArgs[6]; // incoming values from serial msg stored here

const byte simPin   = A0; // this pin goes high when sim is active
const byte platformOnPin = A1; // this pin goes high when motor starts
const byte simMsgPin = 13; // led flashes when msg received
const byte enableServosPin = 10; // this pin low enables servos
boolean isPlatformActive = false;
unsigned long prevMsgTime;

//Array of servo objects
const byte nbrActuators = 6;
Servo servo[nbrActuators];
const byte servoPins[nbrActuators] = {4, 5, 6, 7, 8, 9};

static int zero[nbrActuators] = {0, 0, 0, 0, 0, 0}; // servo offsets in degrees for arms horizontal
static float theta_a[nbrActuators] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

//const float  servo_min = radians(-80), servo_max = radians(80); //maximum servo positions, 0 is horizontal position
const float servo_mult = 1; //// 400 / (PI / 4); // multiplier used for conversion radians->servo pulse in us

const float L1 = 28;       // effective length of servo arm
const float L2 = 200;      // length of base and platform connecting arm
const float z_home = 190;  // height of platform above base, 0 is height of servo arms

void setup() {
  Serial.begin(57600);
  pinMode(simPin, OUTPUT);
  pinMode(platformOnPin, OUTPUT);
  pinMode(simMsgPin, OUTPUT);
  pinMode(enableServosPin, INPUT_PULLUP); 
  digitalWrite(simPin, LOW);
  digitalWrite(platformOnPin, HIGH);
  digitalWrite(simMsgPin, LOW);
  for (int s = 0; s < nbrActuators; s++) {
    servo[s].attach(servoPins[s], MIN, MAX);
    servo[s].write(90);
  }
  /////setPos(locArray);  //set to base position
  delay(700);
  digitalWrite(platformOnPin, LOW);
  Serial.println(F("Platform initialized"));
}

//main control loop, responds to commands from serial port
void loop()
{
  if (Serial.available() > 2) {
    if (Serial.peek() == '\n' || Serial.peek() == '\r')
      Serial.read(); // discard cr/lf
    else {
      if (processShortMessage((Stream*)&Serial)) {
        activatePlatform(true);
        prevMsgTime = millis();
        Serial.print("raw ");
        for (int i = 0; i < 6; i++) {        
          theta_a[i] = getAlpha(rawArgs[i]);    
          Serial.print(int(rawArgs[i]));Serial.print(':'); Serial.print(int( theta_a[i]));Serial.print('\t');         
        }
        Serial.println();
        moveServos();
      }
    }
  }
  if ( millis() - prevMsgTime > 1000) {
    // turn off platform if no recent messages
    activatePlatform(false);
    digitalWrite(simMsgPin, LOW ); // turn off led
  }
}
float getAlpha( float len) // returns angle in degrees
{
  if( len > 500)
    len = len / 3.75; // just in case its chair data!!!
  float r =  acos((len * len + L1 * L1 - L2 * L2) / (2 * len * L1));
  //Serial.print("expresion="); Serial.println((len * len + L1 * L1 - L2 * L2) / (2 * len * L1));
  //Serial.print(", len = "); Serial.print(len);// Serial.print(", L1 = "); Serial.print(L1); Serial.print(", L2 = "); Serial.print(L2);
  //Serial.print(", r= "); Serial.print(r);
  float degrees =  r * RAD_TO_DEG;
  //Serial.print(", degrees = "); Serial.println(degrees);
  return degrees;
}

// moves the platform into position  determined by pe array (z,y,z,roll,pitch,yaw)
void  moveServos() {
  
#define SHOW_SERVO_POS
#ifdef SHOW_SERVO_POS
  Serial.print(F("Servos: "));
#endif
  int servoPos;
  for (int i = 0; i < nbrActuators; i++)
  {
    if (i == INV1 || i == INV2 || i == INV3) {    
      servoPos = constrain(180 - zero[i] - theta_a[i], MIN, MAX);
    }
    else {
      servoPos = constrain(zero[i] + theta_a[i], MIN, MAX);
    }
    servo[i].write(servoPos);
#ifdef SHOW_SERVO_POS
    Serial.print(servoPos); Serial.print('\t');
#endif
  }
#ifdef SHOW_SERVO_POS
  Serial.println();
#endif
}

void activatePlatform( boolean state)
{ 
  //printf("activate = %s ", state? "TRUE":"false");
  if (state !=  isPlatformActive ) {
    if ( state == true && digitalRead(enableServosPin) == LOW ) {
      digitalWrite(platformOnPin, HIGH);
      Serial.print(" ->Platform active");
    }
    else {
      // centerServos();  //  delay(700);
      digitalWrite(platformOnPin, LOW);
      Serial.print("->Platform off");
    }
    isPlatformActive = state;
  }
  // printf(", state = %s\n",state ? "TRUE":"false");
}


// return true is message data is available
boolean  processShortMessage(Stream * s) {
  boolean ret = false; // default indicating invalid message
  if ( s->find("rawArgs")) {
    for (int i = 0; i < 6; i++) {
      rawArgs[i] = s->parseFloat();     
      i == 5 ? Serial.println() : Serial.print(',');
    }
    ret = true;
  }
  printf("ret=%d\n", ret);
  return ret;
}

