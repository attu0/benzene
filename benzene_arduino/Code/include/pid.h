#pragma once
#include <stdint.h>

struct Gains {
  float kp, ki, kd;
  float kff;   // feedforward, PWM counts per (tick/s)
};

// Velocity controller for one wheel. No hardware access: it takes tick counts
// in and returns a PWM value, so it is easy to reason about and test.
class WheelController {
 public:
  void  setTarget(float tps) { target_ = tps; }
  float target() const       { return target_; }
  float velocity() const     { return vel_; }          // filtered ticks/s

  void resetIntegrator()        { integ_ = 0; }
  void resetTicks(int32_t t)    { lastTicks_ = t; }    // call after zeroing encoders

  // Call once per control period. Returns PWM in -255..255.
  int update(int32_t ticks, float dt, const Gains &g);

 private:
  float   target_    = 0;
  float   vel_       = 0;
  float   integ_     = 0;
  int32_t lastTicks_ = 0;
};