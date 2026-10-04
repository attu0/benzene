#include "encoders.h"
#include <Arduino.h>
#include "config.h"

// Same pins and same decoding as the ros_arduino_bridge reference:
//   Left  wheel: A = D2 (PD2), B = D3 (PD3)  -> PCINT2_vect
//   Right wheel: A = A4 (PC4), B = A5 (PC5)  -> PCINT1_vect
// If a wheel counts backwards, flip its ENC_x_SIGN in config.h.

namespace {
volatile int32_t g_left = 0, g_right = 0;
volatile uint8_t g_prevL = 0, g_prevR = 0;

// index = (previous 2-bit state << 2) | current state; value = tick delta
const int8_t QEM[16] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0};

constexpr uint8_t PORTD_MASK = 0b00001100;   // D2, D3
constexpr uint8_t PORTC_MASK = 0b00110000;   // A4, A5

inline uint8_t stateLeft(uint8_t pind)  { return (pind >> 2) & 3; }   // bit0 = D2, bit1 = D3
inline uint8_t stateRight(uint8_t pinc) { return (pinc >> 4) & 3; }   // bit0 = A4, bit1 = A5
}  // namespace

ISR(PCINT2_vect) {   // left wheel (PORTD)
  uint8_t s = stateLeft(PIND);
  g_left += cfg::ENC_L_SIGN * QEM[(g_prevL << 2) | s];
  g_prevL = s;
}

ISR(PCINT1_vect) {   // right wheel (PORTC)
  uint8_t s = stateRight(PINC);
  g_right += cfg::ENC_R_SIGN * QEM[(g_prevR << 2) | s];
  g_prevR = s;
}

namespace encoders {

void init() {
  DDRD  &= ~PORTD_MASK;   // inputs
  PORTD |=  PORTD_MASK;   // pull-ups (harmless for push-pull encoders)
  DDRC  &= ~PORTC_MASK;
  PORTC |=  PORTC_MASK;
  g_prevL = stateLeft(PIND);
  g_prevR = stateRight(PINC);
  PCMSK2 |= PORTD_MASK;
  PCMSK1 |= PORTC_MASK;
  PCICR  |= (1 << PCIE1) | (1 << PCIE2);
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

uint8_t readChannel(uint8_t wheel, uint8_t channel) {
  if (wheel == 0) return (PIND >> (channel ? 3 : 2)) & 1;   // D2 (A) / D3 (B)
  return (PINC >> (channel ? 5 : 4)) & 1;                    // A4 (A) / A5 (B)
}

}  // namespace encoders