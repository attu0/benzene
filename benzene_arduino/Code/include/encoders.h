#pragma once
#include <stdint.h>

// Quadrature decoding (4x) for both wheels, done in a single pin-change ISR.
namespace encoders {
void init();
void snapshot(int32_t &left, int32_t &right);  // consistent read of both counts
void reset();                                  // zero both counts
}