#pragma once
// ---------------------------------------------------------------------------
// config.h  -  every tunable number and pin for the benzene Uno firmware.
// If you only want to retune or rewire, this is the only file you touch.
// ---------------------------------------------------------------------------
#include <Arduino.h>

namespace cfg {

// ----- serial / timing -----
constexpr uint32_t BAUD              = 115200;
constexpr uint32_t CONTROL_PERIOD_US = 20000;   // 50 Hz: PID + telemetry
constexpr uint32_t CMD_TIMEOUT_MS    = 500;     // binary host: no command this long -> stop
constexpr uint32_t TEXT_CMD_TIMEOUT_MS = 2000;  // typed serial commands: longer, you are typing by hand
constexpr int16_t  MAX_TPS           = 3000;    // clamp on commanded ticks/s

// ----- direction fixes (flip if a wheel counts / spins backwards) -----
constexpr int8_t ENC_L_SIGN     = 1;
constexpr int8_t ENC_R_SIGN     = 1;
constexpr bool   MOTOR_L_INVERT = false;
constexpr bool   MOTOR_R_INVERT = false;

// ----- L298N pins: SAME as the ros_arduino_bridge reference (known to run on this wiring) -----
// Style used here: PWM on the IN pins, the two EN pins are simply held HIGH.
// These must be PWM-capable pins (3, 5, 6, 9, 10, 11).
constexpr bool    PWM_ON_INPUTS = true;
constexpr uint8_t L_FWD = 10, L_BWD = 6, L_EN = 13;
constexpr uint8_t R_FWD = 9,  R_BWD = 5, R_EN = 12;
// Alternative (the first wiring diagram): PWM on ENA/ENB, plain direction on IN1..IN4:
//   PWM_ON_INPUTS = false;  L_EN = 5, L_FWD = 11, L_BWD = 10;  R_EN = 6, R_FWD = 8, R_BWD = 9;
// In that mode ENA/ENB carry the PWM, so the ENA/ENB jumper caps MUST be removed.
// The Uno does not touch ANY motor pin until the first non-zero motor command.

// ----- encoder pins: also the same as the reference -----
// Fixed by encoders.cpp (pin-change interrupts, one ISR per wheel):
//   Left  : A = D2, B = D3   (PORTD, PCINT2)
//   Right : A = A4, B = A5   (PORTC, PCINT1)
// Changing these means editing encoders.cpp too.
// A4/A5 are the Uno's I2C pins; fine, because the IMU lives on the Pi.

// ----- PID starting values: TUNE THESE (live via SET_PID message) -----
constexpr float KP  = 0.10f;
constexpr float KI  = 0.50f;
constexpr float KD  = 0.00f;
constexpr float KFF = 0.10f;   // feedforward: PWM counts per (tick/s)
constexpr float VEL_FILTER_ALPHA = 0.5f;   // 1.0 = no smoothing
constexpr int   PWM_MIN = 0;   // smallest PWM that moves a wheel (0 = off)

}  // namespace cfg