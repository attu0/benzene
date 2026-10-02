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
constexpr uint32_t CMD_TIMEOUT_MS    = 500;     // no command this long -> stop
constexpr int16_t  MAX_TPS           = 3000;    // clamp on commanded ticks/s

// ----- direction fixes (flip if a wheel counts / spins backwards) -----
constexpr int8_t ENC_L_SIGN     = 1;
constexpr int8_t ENC_R_SIGN     = 1;
constexpr bool   MOTOR_L_INVERT = false;
constexpr bool   MOTOR_R_INVERT = false;

// ----- L298N pins -----
constexpr uint8_t L_EN = 9,  L_IN1 = 7,  L_IN2 = 8;    // ENA must be PWM (D9)
constexpr uint8_t R_EN = 10, R_IN3 = 11, R_IN4 = 12;   // ENB must be PWM (D10)

// ----- encoder pins -----
// NOTE: fixed by encoders.cpp (one pin-change ISR on PORTD).
//   Left  A = D2, B = D4
//   Right A = D3, B = D5
// Changing these means editing encoders.cpp too.

// ----- PID starting values: TUNE THESE (live via SET_PID message) -----
constexpr float KP  = 0.10f;
constexpr float KI  = 0.50f;
constexpr float KD  = 0.00f;
constexpr float KFF = 0.10f;   // feedforward: PWM counts per (tick/s)
constexpr float VEL_FILTER_ALPHA = 0.5f;   // 1.0 = no smoothing
constexpr int   PWM_MIN = 0;   // smallest PWM that moves a wheel (0 = off)

}  // namespace cfg