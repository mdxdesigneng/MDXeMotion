/* Arduino Controlled Rotary Stewart Platform
   Responds to normalized raw  middleware messsages  
*/

#include <Servo.h>
#include <Wire.h>
#include "platformMsgs.h"
#include "printf.h"

//MIN and MAX PWM pulse sizes, they can be adjusted to calibrate servos
#define MAX 2450
#define MIN 550

//Positions of servos mounted in opposite direction
#define INV1 1
#define INV2 3
#define INV3 5

//constants for computation of positions of connection points
//#define deg2rad 180/PI
#define degrees(rad) ((rad)*RAD_TO_DEG)

const byte simPin   = A0; // this pin goes high when sim is active
const byte platformOnPin = A1; // this pin goes high when motor starts
boolean isPlatformActive = false;
unsigned long prevMsgTime;

//Array of servo objects
const byte nbrActuators = 6;
Servo servo[nbrActuators];
const byte servoPins[nbrActuators] = {9,4, 5, 6, 7, 8};

static int zero[nbrActuators] = {0, 0, 0, 0, 0, 0}; // servo offset tp position arms right angle to connecting rod.

static byte servo_pos[nbrActuators]; // current servo angle in degrees

const float  SERVO_MIN = 15, SERVO_MAX = 165; //min and max servo angles
const float  SERVO_MIN_RAD = radians(SERVO_MIN);
const float  SERVO_MAX_RAD = radians(SERVO_MAX);

static float normValues[nbrActuators]; // normalized values received from middleware

void setup() {
  Serial.begin(57600);  
  pinMode(simPin, OUTPUT);
  pinMode(platformOnPin, OUTPUT);
  digitalWrite(simPin, LOW);
  digitalWrite(platformOnPin, HIGH);
  for (int s = 0; s < nbrActuators; s++) {
    servo[s].attach(servoPins[s], MIN, MAX);
    servo_pos[s] = 90; // center servo pos
    normValues[s] = 0;
  }
  setPos(normValues);  //set to base position
  delay(700);
  digitalWrite(platformOnPin, LOW);
  Serial.println(F("PlatformSim3"));
  Serial.println(F("Platform initialized"));
}

//function calculating needed servo rotation angle in degrees for a given offset
  // offset is a float within the range of -1.0 and +1.0
  // calibrating servos will improve accuracy
  int getTheta(float offset, int currentAngle)
  {
    int iter = 0;
    float min = SERVO_MIN_RAD;  // min angle in radians
    float max = SERVO_MAX_RAD;  // max angle in radians
    float theta = radians(currentAngle);
    float CosTheta;
    float diff;
    long startime = micros();
    while (iter < 20) {      
      CosTheta = cos(theta);
      diff = CosTheta;     
      // if diff is close to desired offset, return the angle
      if (abs(diff - offset) < 0.01) {
        break;
      }  
      // else, chop the searched space in half, and try next value
      if (diff < offset) {
        max = theta;
      } else {
        min = theta;
      }
      iter++;
      if (max == SERVO_MIN_RAD || min == SERVO_MAX_RAD) {
        Serial.print(" max!!!=");Serial.println(max);
        break;
      }
      theta = min + (max - min) / 2;
    }
    long endtime = micros();
    //Serial.print(" dur=");Serial.print(endtime-startime);
    //Serial.print(" iter=");Serial.print(iter); Serial.print(", ");
    return degrees(theta);
  }


// moves the platform into position  determined by pe array (z,y,z,roll,pitch,yaw)
unsigned char setPos(float argArray[]) {

//#define SHOW_SERVO_POS
#define SHOW_SERVO_CSV

  for (int i = 0; i < nbrActuators; i++){     
    servo_pos[i] = getTheta(argArray[i], servo_pos[i]);   
  }
  runningAverage(servo_pos); // smooth values in servo_pos array
  
  for (int i = 0; i < nbrActuators; i++){
    int pos;
    if (i == INV1 || i == INV2 || i == INV3) {     
      pos = constrain(180 - (servo_pos[i] + zero[i]), SERVO_MIN, SERVO_MAX);         
    }
    else {
      pos = constrain(servo_pos[i] + zero[i], SERVO_MIN, SERVO_MAX);
    }
    servo[i].write(pos);
#ifdef SHOW_SERVO_CSV
     Serial.print(pos); Serial.print(",");
#endif    
#ifdef SHOW_SERVO_POS
    Serial.print("Servo "); Serial.print(i);   
    Serial.print(": arg="); Serial.print( argArray[i]);
    Serial.print(", angle="); Serial.print( servo_pos[i]);
    Serial.print(" ("); Serial.print(pos); Serial.println(")");
#endif
  }  
  #ifdef SHOW_SERVO_CSV
     for (int i = 0; i < nbrActuators; i++){   
       Serial.print(argArray[i]); Serial.print(",");
     }
     Serial.println();
#endif
}

//main control loop, responds to commands from serial port
void loop()
{
  if (Serial.available() > 2) {
    if (Serial.peek() == '\n' || Serial.peek() == '\r')
      Serial.read(); // discard cr/lf
    else {
      msgErr_t ret = processMessage((Stream*)&Serial, normValues );
      //msgErr_t ret = processRawArgs((Stream*)&Serial, normValues );
      if ( ret == NO_ERROR) {
        setPos(normValues);      
      }
      else {
        Serial.println(msgErrStr[ret]);
      }
    }
  }
    if ( millis() - prevMsgTime > 1000) {
      // turn off platform if no recent messages
      activatePlatform(false);    
    }    
}

void activatePlatform( boolean state)
{  
  //printf("activate = %s ", state? "TRUE":"false");
  if(state !=  isPlatformActive ) {
    if( state == true){
       digitalWrite(platformOnPin, HIGH);
       Serial.print(" ->Platform active");
    }
    else {
      // centerServos();
     //  delay(700);
       digitalWrite(platformOnPin, LOW);
       Serial.println("->Platform off"); 
    }  
    isPlatformActive = state;
  }
 // printf(", state = %s\n",state ? "TRUE":"false");    
}

void runningAverage(byte *values) {
  const byte SAMPLE_SIZE = 4;
  static byte samples[6][SAMPLE_SIZE]; 
  static byte index = 0;
  static int sum[6] = {0};
  static byte count = 1;
 
  // keep sum updated to improve speed.
  //Serial.print("index= "); Serial.println(index) ;  Serial.print(", count= "); Serial.println(count);  ;   
  for(byte i=0; i < 6; i++) {
/*
   Serial.print("before: i= "); Serial.print(i);  
   Serial.print(": sum[i]="); Serial.print( sum[i]); 
    Serial.print(": samples[i]="); Serial.print( samples[i][index]);
    Serial.print(", value="); Serial.println( values[i]);
*/  
    
    sum[i] -= samples[i][index];
    samples[i][index] = values[i];
    sum[i] += samples[i][index];         
    values[i] = sum[i] / count;
/*
    
   Serial.print("after: i= "); Serial.print(i);   
    Serial.print(": sum[i]="); Serial.print( sum[i]);
    Serial.print(": samples[i]="); Serial.print( samples[i][index]);
    Serial.print(", value="); Serial.println( values[i]);
*/    
  }
  if(++index == SAMPLE_SIZE) index=0;     
  if (count < SAMPLE_SIZE) count++;
}

