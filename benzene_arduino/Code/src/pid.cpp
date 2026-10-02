#include "pid.h"
#include <math.h>
#include "config.h"

int WheelController::update(int32_t ticks, float dt, const Gains &g) {
  float raw = (ticks - lastTicks_) / dt;
  lastTicks_ = ticks;
  float prevVel = vel_;
  vel_ += cfg::VEL_FILTER_ALPHA * (raw - vel_);

  if (target_ == 0.0f) {          // stopped: no windup, coast
    integ_ = 0;
    return 0;
  }

  float err = target_ - vel_;
  float dv  = (vel_ - prevVel) / dt;            // derivative on measurement
  float u   = g.kff * target_ + g.kp * err + g.ki * integ_ - g.kd * dv;
  if (fabsf(u) < 255.0f) integ_ += err * dt;    // anti-windup

  int pwm = (int)u;
  if (pwm > 255) pwm = 255;
  if (pwm < -255) pwm = -255;
  if (pwm != 0 && abs(pwm) < cfg::PWM_MIN) pwm = (pwm > 0) ? cfg::PWM_MIN : -cfg::PWM_MIN;
  return pwm;
}