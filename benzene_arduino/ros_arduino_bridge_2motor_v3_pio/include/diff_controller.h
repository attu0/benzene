#ifndef DIFF_CONTROLLER_H
#define DIFF_CONTROLLER_H

#include "config.h"
#include "commands.h"
#include "encoder_driver.h"
#include "motor_driver.h"

/* Functions and type-defs for PID control.

   Taken mostly from Mike Ferguson's ArbotiX code which lives at:

   http://vanadium-ros-pkg.googlecode.com/svn/trunk/arbotix/
*/

/* PID setpoint info For a Motor */
typedef struct {
  double TargetTicksPerFrame;    // target speed in ticks per frame
  long Encoder;                  // encoder count
  long PrevEnc;                  // last encoder count

  /*
  * Using previous input (PrevInput) instead of PrevError to avoid derivative kick,
  * see http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-derivative-kick/
  */
  int PrevInput;                // last input

  /*
  * Using integrated term (ITerm) instead of integrated error (Ierror),
  * to allow tuning changes,
  * see http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-tuning-changes/
  *
  * long (not int): an int is only 16 bits on AVR and would overflow.
  */
  long ITerm;                   // integrated term

  /*
  * Last motor setting, kept at higher resolution: this holds PWM * Ko.
  * The real PWM is output / Ko (see updatePID). Keeping the extra
  * resolution removes the dead zone that integer division by Ko used to
  * create (an error smaller than Ko/Kp counts used to add nothing).
  */
  long output;
}
SetPointInfo;

SetPointInfo leftPID, rightPID;

/* PID Parameters
   Ko must stay > 0. Change gains (the `u` command) only while the robot
   is stopped: `output` is scaled by Ko. */
int Kp = 10;
int Kd = 10;
int Ki = 0;
int Ko = 50;

unsigned char moving = 0; // is the base in motion?

/*
* Initialize PID variables to zero to prevent startup spikes
* when turning PID on to start moving
* In particular, assign both Encoder and PrevEnc the current encoder value
* See http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-initialization/
* Note that the assumption here is that PID is only turned on
* when going from stop to moving, that's why we can init everything on zero.
*/
void resetPID(){
   leftPID.TargetTicksPerFrame = 0.0;
   leftPID.Encoder = readEncoder(LEFT);
   leftPID.PrevEnc = leftPID.Encoder;
   leftPID.output = 0;
   leftPID.PrevInput = 0;
   leftPID.ITerm = 0;

   rightPID.TargetTicksPerFrame = 0.0;
   rightPID.Encoder = readEncoder(RIGHT);
   rightPID.PrevEnc = rightPID.Encoder;
   rightPID.output = 0;
   rightPID.PrevInput = 0;
   rightPID.ITerm = 0;
}

/* PID routine to compute the next motor commands.
   Velocity-form PID: every frame the correction is ADDED to the output.
   p->output holds PWM * Ko, so no precision is lost to integer division. */
void doPID(SetPointInfo * p) {
  long Perror;
  long out;
  int input;

  input = p->Encoder - p->PrevEnc;
  Perror = p->TargetTicksPerFrame - input;
  p->PrevEnc = p->Encoder;

  /*
  * Derivative on the measurement (no derivative kick) and an integrated
  * term that allows tuning changes:
  * see http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-derivative-kick/
  * see http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-tuning-changes/
  */
  out = p->output + ((long)Kp * Perror - (long)Kd * (input - p->PrevInput) + p->ITerm);

  // Accumulate Integral error *or* Limit output.
  // Stop accumulating when output saturates
  long limit = (long)MAX_PWM * Ko;
  if (out >= limit)
    out = limit;
  else if (out <= -limit)
    out = -limit;
  else
    p->ITerm += (long)Ki * Perror;

  p->output = out;
  p->PrevInput = input;
}

/* Read the encoder values and call the PID routine */
void updatePID() {
  /* Read the encoders */
  leftPID.Encoder = readEncoder(LEFT);
  rightPID.Encoder = readEncoder(RIGHT);

  /* If we're not moving there is nothing more to do */
  if (!moving){
    /*
    * Reset PIDs once, to prevent startup spikes,
    * see http://brettbeauregard.com/blog/2011/04/improving-the-beginner%E2%80%99s-pid-initialization/
    * PrevInput is considered a good proxy to detect
    * whether reset has already happened
    */
    if (leftPID.PrevInput != 0 || rightPID.PrevInput != 0) resetPID();
    return;
  }

  /* Compute PID update for each motor */
  doPID(&rightPID);
  doPID(&leftPID);

  /* Set the motor speeds accordingly (output is PWM * Ko) */
  setMotorSpeeds((int)(leftPID.output / Ko), (int)(rightPID.output / Ko));
}


#endif