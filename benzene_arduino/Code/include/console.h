#pragma once
#include <stdint.h>

// ---------------------------------------------------------------------------
// Typed serial commands, for testing from a serial monitor (in the spirit of
// the andino firmware). One command per line, values separated by spaces.
//
//   e                 read encoder ticks          -> "left right"
//   v                 read measured speed         -> "left right"  (ticks/s)
//   r                 reset encoder ticks to 0    -> OK
//   d <w> <c>         raw encoder pin level       -> 0 or 1
//                       w: 0 = left, 1 = right   c: 0 = C1, 1 = C2
//   m <l> <r>         closed-loop speed targets, ticks/s            -> OK
//   o <l> <r>         open-loop raw PWM, -255..255 (bypasses PID)   -> OK
//   u <kp> <ki> <kd> [kff]   set PID gains                          -> OK
//   ?                 list commands
//
// Anything it does not understand answers "ERR". Motors stop by themselves
// TEXT_CMD_TIMEOUT_MS after the last m/o command.
// ---------------------------------------------------------------------------
namespace console {

struct Actions {
  void (*setSpeed)(int16_t left_tps, int16_t right_tps);
  void (*setPwm)(int16_t left_pwm, int16_t right_pwm);
  void (*resetEncoders)();
  void (*setGains)(float kp, float ki, float kd, float kff);   // kff < 0 = leave unchanged
  void (*getVelocity)(int16_t &left_tps, int16_t &right_tps);
};

void init(const Actions &a);
void handleLine(char *line);   // one command line, newline already stripped

}  // namespace console