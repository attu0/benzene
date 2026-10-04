#include "motors.h"
#include <Arduino.h>
#include "config.h"

// L298N driver.
//  - The Uno leaves every motor pin untouched (high impedance) until the FIRST
//    non-zero command, like the ros_arduino_bridge reference. Nothing is driven at boot.
//  - A pin is only rewritten when its value changes (no 50 Hz rewriting).
//  - Build with -DNO_MOTORS (env:uno_encoders_only) to disable all motor output.

namespace motors {
namespace {

struct SidePins { uint8_t en, fwd, bwd; };

SidePins pinsOf(Side s) {
  return (s == Side::Left) ? SidePins{cfg::L_EN, cfg::L_FWD, cfg::L_BWD}
                           : SidePins{cfg::R_EN, cfg::R_FWD, cfg::R_BWD};
}

bool g_armed = false;
int  g_last[2] = {0, 0};     // last value written per side (after inversion)

void arm() {
  if (g_armed) return;
  const SidePins sides[2] = {pinsOf(Side::Left), pinsOf(Side::Right)};
  for (const SidePins &p : sides) {
    pinMode(p.fwd, OUTPUT);
    pinMode(p.bwd, OUTPUT);
    pinMode(p.en, OUTPUT);
    digitalWrite(p.fwd, LOW);
    digitalWrite(p.bwd, LOW);
    digitalWrite(p.en, cfg::PWM_ON_INPUTS ? HIGH : LOW);
  }
  g_armed = true;
}

void write(const SidePins &p, int pwm) {
  if (cfg::PWM_ON_INPUTS) {                       // EN held HIGH, PWM on the IN pins
    if (pwm > 0)      { analogWrite(p.fwd, pwm);  analogWrite(p.bwd, 0); }
    else if (pwm < 0) { analogWrite(p.bwd, -pwm); analogWrite(p.fwd, 0); }
    else              { analogWrite(p.fwd, 0);    analogWrite(p.bwd, 0); }
  } else {                                        // PWM on EN, plain direction pins
    if (pwm > 0)      { digitalWrite(p.fwd, HIGH); digitalWrite(p.bwd, LOW);  analogWrite(p.en, pwm); }
    else if (pwm < 0) { digitalWrite(p.fwd, LOW);  digitalWrite(p.bwd, HIGH); analogWrite(p.en, -pwm); }
    else              { digitalWrite(p.fwd, LOW);  digitalWrite(p.bwd, LOW);  analogWrite(p.en, 0); }
  }
}

}  // namespace

void init() {
  g_armed = false;
  g_last[0] = g_last[1] = 0;
}

void set(Side side, int pwm) {
#ifdef NO_MOTORS
  (void)side; (void)pwm;
  return;
#else
  pwm = constrain(pwm, -255, 255);
  const bool left = (side == Side::Left);
  if (left ? cfg::MOTOR_L_INVERT : cfg::MOTOR_R_INVERT) pwm = -pwm;
  const uint8_t idx = left ? 0 : 1;

  if (!g_armed) {
    if (pwm == 0) return;                         // nothing to do, leave pins alone
    arm();
  }
  if (pwm == g_last[idx]) return;                 // unchanged: do not touch the pins
  g_last[idx] = pwm;
  write(pinsOf(side), pwm);
#endif
}

void stopAll() {
  set(Side::Left, 0);
  set(Side::Right, 0);
}

}  // namespace motors