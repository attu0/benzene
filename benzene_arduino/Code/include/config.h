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

// ----- L298N pins (from the wiring diagram) -----
constexpr uint8_t L_EN = 5, L_IN1 = 11, L_IN2 = 10;    // ENA must be a PWM pin
constexpr uint8_t R_EN = 6, R_IN3 = 8,  R_IN4 = 9;     // ENB must be a PWM pin

// ----- encoder pins (from the wiring diagram) -----
// NOTE: fixed by encoders.cpp (pin-change interrupts, one ISR per wheel).
//   Left  : C1 = A4, C2 = A5   (PORTC, PCINT1)
//   Right : C1 = D3, C2 = D2   (PORTD, PCINT2)
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