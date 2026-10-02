#include "motors.h"
#include <Arduino.h>
#include "config.h"

namespace motors {

void init() {
  const uint8_t pins[] = {cfg::L_EN, cfg::L_IN1, cfg::L_IN2,
                          cfg::R_EN, cfg::R_IN3, cfg::R_IN4};
  for (uint8_t p : pins) pinMode(p, OUTPUT);
  // Timer1 (D9/D10) prescaler 8 -> ~3.9 kHz PWM, quieter than the 490 Hz default.
  TCCR1B = (TCCR1B & 0xF8) | 0x02;
  stopAll();
}

void set(Side side, int pwm) {
  const bool left = (side == Side::Left);
  pwm = constrain(pwm, -255, 255);
  if (left ? cfg::MOTOR_L_INVERT : cfg::MOTOR_R_INVERT) pwm = -pwm;

  const uint8_t en = left ? cfg::L_EN  : cfg::R_EN;
  const uint8_t a  = left ? cfg::L_IN1 : cfg::R_IN3;
  const uint8_t b  = left ? cfg::L_IN2 : cfg::R_IN4;

  if (pwm > 0)      { digitalWrite(a, HIGH); digitalWrite(b, LOW);  analogWrite(en, pwm); }
  else if (pwm < 0) { digitalWrite(a, LOW);  digitalWrite(b, HIGH); analogWrite(en, -pwm); }
  else              { digitalWrite(a, LOW);  digitalWrite(b, LOW);  analogWrite(en, 0); }
}

void stopAll() {
  set(Side::Left, 0);
  set(Side::Right, 0);
}

}  // namespace motors