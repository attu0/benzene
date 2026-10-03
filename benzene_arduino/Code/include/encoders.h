#pragma once
#include <stdint.h>

// Quadrature decoding (4x) for both wheels, done with one pin-change ISR per wheel.
namespace encoders {
void init();
void snapshot(int32_t &left, int32_t &right);  // consistent read of both counts
void reset();                                  // zero both counts
// Raw pin level for wiring checks. wheel: 0 = left, 1 = right; channel: 0 = C1, 1 = C2.
uint8_t readChannel(uint8_t wheel, uint8_t channel);
}