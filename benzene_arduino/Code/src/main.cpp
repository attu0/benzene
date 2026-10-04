// main.cpp - wiring only: init the modules, run the 50 Hz control loop.
#include <Arduino.h>
#include "config.h"
#include "console.h"
#include "encoders.h"
#include "motors.h"
#include "pid.h"
#include "protocol.h"

namespace {

Gains           g_gains{cfg::KP, cfg::KI, cfg::KD, cfg::KFF};
WheelController g_left, g_right;

uint32_t g_lastCmdMs = 0;
uint32_t g_timeoutMs = cfg::CMD_TIMEOUT_MS;
bool     g_watchdogTripped = true;   // stays tripped until the first command
bool     g_openLoop = false;         // true: 'o' command drives raw PWM, PID bypassed
int      g_pwmL = 0, g_pwmR = 0;
uint32_t g_lastLoopUs = 0;

float clampTps(int16_t v) {
  if (v > cfg::MAX_TPS)  return cfg::MAX_TPS;
  if (v < -cfg::MAX_TPS) return -cfg::MAX_TPS;
  return v;
}

void feedWatchdog(uint32_t timeoutMs) {
  g_timeoutMs = timeoutMs;
  g_lastCmdMs = millis();
  g_watchdogTripped = false;
}

void applyTargets(int16_t l, int16_t r, uint32_t timeoutMs) {
  g_openLoop = false;
  g_left.setTarget(clampTps(l));
  g_right.setTarget(clampTps(r));
  feedWatchdog(timeoutMs);
}

void resetEncoders() {
  encoders::reset();
  g_left.resetTicks(0);
  g_right.resetTicks(0);
}

void setGains(float kp, float ki, float kd, float kff) {
  g_gains.kp = kp;
  g_gains.ki = ki;
  g_gains.kd = kd;
  if (kff >= 0) g_gains.kff = kff;
  g_left.resetIntegrator();
  g_right.resetIntegrator();
}

// ----- binary protocol callbacks -----
void onCmdVel(int16_t l, int16_t r) { applyTargets(l, r, cfg::CMD_TIMEOUT_MS); }
void onSetPid(float kp, float ki, float kd) { setGains(kp, ki, kd, -1.0f); }

// ----- typed console callbacks -----
void textSetSpeed(int16_t l, int16_t r) { applyTargets(l, r, cfg::TEXT_CMD_TIMEOUT_MS); }

void textSetPwm(int16_t l, int16_t r) {
  g_openLoop = true;
  g_pwmL = l;
  g_pwmR = r;
  g_left.setTarget(0);
  g_right.setTarget(0);
  feedWatchdog(cfg::TEXT_CMD_TIMEOUT_MS);
}

void textGetVelocity(int16_t &l, int16_t &r) {
  l = (int16_t)g_left.velocity();
  r = (int16_t)g_right.velocity();
}

}  // namespace

void setup() {
  protocol::init({onCmdVel, resetEncoders, onSetPid, console::handleLine});
  console::init({textSetSpeed, textSetPwm, resetEncoders, setGains, textGetVelocity});
  encoders::init();
  motors::init();
  g_lastLoopUs = micros();
  Serial.println(F("benzene boot"));   // if you see this mid-session, the Uno RESET (power/USB glitch)
}

void loop() {
  protocol::poll();

  uint32_t nowUs = micros();
  if ((uint32_t)(nowUs - g_lastLoopUs) < cfg::CONTROL_PERIOD_US) return;
  float dt = (nowUs - g_lastLoopUs) * 1e-6f;
  g_lastLoopUs = nowUs;

  // watchdog: nobody told us what to do recently -> stop
  if (!g_watchdogTripped && (millis() - g_lastCmdMs) > g_timeoutMs) {
    g_watchdogTripped = true;
    g_openLoop = false;
    g_left.setTarget(0);
    g_right.setTarget(0);
  }

  int32_t tl, tr;
  encoders::snapshot(tl, tr);
  int pwmL = g_left.update(tl, dt, g_gains);    // always runs: keeps velocity estimate alive
  int pwmR = g_right.update(tr, dt, g_gains);
  if (g_openLoop) {
    pwmL = g_pwmL;
    pwmR = g_pwmR;
  }
  motors::set(Side::Left,  pwmL);
  motors::set(Side::Right, pwmR);

  if (protocol::streaming()) {
    protocol::StateMsg s;
    s.stamp_us = nowUs;
    s.ticks_l  = tl;
    s.ticks_r  = tr;
    s.vel_l    = (int16_t)g_left.velocity();
    s.vel_r    = (int16_t)g_right.velocity();
    s.flags    = g_watchdogTripped ? protocol::FLAG_WATCHDOG : 0;
    protocol::sendState(s);
  }
}