/***************************************************************
   Motor driver function definitions (upstream interface)
   *************************************************************/

#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include "config.h"

#ifdef L298N_EN_PWM_DRIVER
  // Physical RIGHT motor
  #define RIGHT_MOTOR_ENABLE    5   // PWM
  #define RIGHT_MOTOR_FORWARD   9
  #define RIGHT_MOTOR_BACKWARD  8

  // Physical LEFT motor
  #define LEFT_MOTOR_ENABLE     6   // PWM
  #define LEFT_MOTOR_FORWARD    10
  #define LEFT_MOTOR_BACKWARD   11
#endif

void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);

#endif
