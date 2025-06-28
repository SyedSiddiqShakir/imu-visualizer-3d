#include "Arduino_BMI270_BMM150.h"

float x, y, z;
int degreesX = 0;
int degreesY = 0;
int prevDegreesX = 999; // force initial transmission
int prevDegreesY = 999;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
}

void loop() {
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    
    // calculate tilt angles from accelerometer data
    // convert to degrees (approximate)
    degreesX = constrain((int)(asin(x) * 180.0 / PI), -90, 90);
    degreesY = constrain((int)(asin(y) * 180.0 / PI), -90, 90);
    
    // send X-axis data if it changed
    if (degreesX != prevDegreesX) {
      if (degreesX > 0) {
        Serial.print("Tilting up ");
        Serial.print(degreesX);
        Serial.println(" degrees");
      } else if (degreesX < 0) {
        Serial.print("Tilting down ");
        Serial.print(-degreesX); // send positive value
        Serial.println(" degrees");
      } else {
        Serial.println("Tilting up 0 degrees");
      }
      prevDegreesX = degreesX;
    }
    
    // send Y-axis data if it changed
    if (degreesY != prevDegreesY) {
      if (degreesY > 0) {
        Serial.print("Tilting left ");
        Serial.print(degreesY);
        Serial.println(" degrees");
      } else if (degreesY < 0) {
        Serial.print("Tilting right ");
        Serial.print(-degreesY); // send positive value
        Serial.println(" degrees");
      } else {
        Serial.println("Tilting left 0 degrees");
      }
      prevDegreesY = degreesY;
    }
  }
  
  delay(50); // ~20Hz update rate
}