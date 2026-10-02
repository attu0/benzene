#include "encoders.h"
#include <Arduino.h>
#include "config.h"

namespace {
volatile int32_t g_left = 0, g_right = 0;
volatile uint8_t g_prevL = 0, g_prevR = 0;

// index = (previous 2-bit AB state << 2) | current state; value = tick delta
const int8_t QEM[16] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0};

constexpr uint8_t PORTD_MASK = 0b00111100;   // D2..D5

inline uint8_t stateLeft(uint8_t p)  { return (((p >> 2) & 1) << 1) | ((p >> 4) & 1); }  // A=D2 B=D4
inline uint8_t stateRight(uint8_t p) { return (((p >> 3) & 1) << 1) | ((p >> 5) & 1); }  // A=D3 B=D5
}  // namespace

ISR(PCINT2_vect) {
  uint8_t p = PIND;
  uint8_t l = stateLeft(p);
  uint8_t r = stateRight(p);
  g_left  += cfg::ENC_L_SIGN * QEM[(g_prevL << 2) | l];
  g_right += cfg::ENC_R_SIGN * QEM[(g_prevR << 2) | r];
  g_prevL = l;
  g_prevR = r;
}

namespace encoders {

void init() {
  DDRD  &= ~PORTD_MASK;   // inputs
  PORTD |=  PORTD_MASK;   // pull-ups (harmless for push-pull encoders)
  uint8_t p = PIND;
  g_prevL = stateLeft(p);
  g_prevR = stateRight(p);
  PCICR  |= (1 << PCIE2);
  PCMSK2 |= PORTD_MASK;
}

void snapshot(int32_t &left, int32_t &right) {
  noInterrupts();
  left  = g_left;
  right = g_right;
  interrupts();
}

void reset() {
  noInterrupts();
  g_left = 0;
  g_right = 0;
  interrupts();
}

}  // namespace encoders