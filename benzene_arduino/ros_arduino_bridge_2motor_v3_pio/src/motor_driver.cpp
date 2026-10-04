/***************************************************************
   Motor driver definitions
   *************************************************************/

#include <Arduino.h>
#include "config.h"
#include "commands.h"
#include "motor_driver.h"

#ifdef USE_BASE

#ifdef L298N_EN_PWM_DRIVER

/* Sign convention (kept from V3, verified on the robot):
     spd > 0  -> motor shaft CLOCKWISE        (FORWARD pin LOW,  BACKWARD pin HIGH)
     spd < 0  -> motor shaft COUNTER-CLOCKWISE (FORWARD pin HIGH, BACKWARD pin LOW)
   This is identical for LEFT and RIGHT, so "+,+" drives the robot forward. */

void initMotorController() {
  pinMode(RIGHT_MOTOR_ENABLE, OUTPUT);
  pinMode(RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(RIGHT_MOTOR_BACKWARD, OUTPUT);

  pinMode(LEFT_MOTOR_ENABLE, OUTPUT);
  pinMode(LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(LEFT_MOTOR_BACKWARD, OUTPUT);

  setMotorSpeeds(0, 0);
}

void setMotorSpeed(int i, int spd) {
  uint8_t en, fwd, bwd;

  if (i == LEFT) {
    en = LEFT_MOTOR_ENABLE;
    fwd = LEFT_MOTOR_FORWARD;
    bwd = LEFT_MOTOR_BACKWARD;
  } else {
    en = RIGHT_MOTOR_ENABLE;
    fwd = RIGHT_MOTOR_FORWARD;
    bwd = RIGHT_MOTOR_BACKWARD;
  }

  spd = constrain(spd, -MAX_PWM, MAX_PWM);

  if (spd > 0) {
    digitalWrite(fwd, LOW);
    digitalWrite(bwd, HIGH);
    analogWrite(en, spd);
  } else if (spd < 0) {
    digitalWrite(fwd, HIGH);
    digitalWrite(bwd, LOW);
    analogWrite(en, -spd);
  } else {
    analogWrite(en, 0);
    digitalWrite(fwd, LOW);
    digitalWrite(bwd, LOW);
  }
}

void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  setMotorSpeed(LEFT, leftSpeed);
  setMotorSpeed(RIGHT, rightSpeed);
}

#else
  #error A motor driver must be selected!
#endif

#endif
