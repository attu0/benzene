#pragma once
#include <stdint.h>

// L298N driver: signed PWM per side. Pins are untouched until the first non-zero command.
enum class Side : uint8_t { Left, Right };

namespace motors {
void init();
void set(Side side, int pwm);   // -255..255, 0 = coast
void stopAll();
}