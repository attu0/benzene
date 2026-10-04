/* *************************************************************
   Encoder definitions

   Both encoders are decoded in pin-change interrupts (upstream
   approach), so no ticks are lost while the main loop is busy
   parsing serial input.
   ************************************************************ */

#include <Arduino.h>
#include "config.h"
#include "commands.h"
#include "encoder_driver.h"

#ifdef USE_BASE

#ifdef ARDUINO_ENC_COUNTER

volatile long left_enc_pos = 0L;
volatile long right_enc_pos = 0L;

/* Quadrature lookup table, index = (previous_state << 2) | current_state,
   where state = (A << 1) | B. Same counting sign as the V3 code. */
static const int8_t ENC_STATES[] = {0,1,-1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0};

static const int8_t LEFT_SIGN  = LEFT_ENC_INVERT  ? -1 : 1;
static const int8_t RIGHT_SIGN = RIGHT_ENC_INVERT ? -1 : 1;

static volatile uint8_t right_last = 0;   // PORTD state history
static volatile uint8_t left_last  = 0;   // PORTC state history

static inline uint8_t readRightState() {
  return (((PIND >> RIGHT_ENC_PIN_A) & 1) << 1) | ((PIND >> RIGHT_ENC_PIN_B) & 1);
}

static inline uint8_t readLeftState() {
  return (((PINC >> LEFT_ENC_PIN_A) & 1) << 1) | ((PINC >> LEFT_ENC_PIN_B) & 1);
}

/* PORTD pins (D2/D3) -> physical RIGHT wheel */
ISR(PCINT2_vect) {
  right_last = ((right_last << 2) | readRightState()) & 0x0f;
  right_enc_pos += RIGHT_SIGN * ENC_STATES[right_last];
}

/* PORTC pins (A4/A5) -> physical LEFT wheel */
ISR(PCINT1_vect) {
  left_last = ((left_last << 2) | readLeftState()) & 0x0f;
  left_enc_pos += LEFT_SIGN * ENC_STATES[left_last];
}

void initEncoders() {
  // inputs with pull-ups
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);

  // start from the current pin state so the first edge isn't a bogus tick
  right_last = readRightState();
  left_last  = readLeftState();

  // listen to the encoder pins only
  PCMSK2 |= (1 << RIGHT_ENC_PIN_A) | (1 << RIGHT_ENC_PIN_B);
  PCMSK1 |= (1 << LEFT_ENC_PIN_A)  | (1 << LEFT_ENC_PIN_B);

  // clear stale flags, then enable PCINT1 (PORTC) and PCINT2 (PORTD)
  PCIFR |= (1 << PCIF1) | (1 << PCIF2);
  PCICR |= (1 << PCIE1) | (1 << PCIE2);
}

/* 32-bit reads are not atomic on AVR, so guard against the ISR. */
long readEncoder(int i) {
  uint8_t sreg = SREG;
  cli();
  long v = (i == LEFT) ? left_enc_pos : right_enc_pos;
  SREG = sreg;
  return v;
}

void resetEncoder(int i) {
  uint8_t sreg = SREG;
  cli();
  if (i == LEFT) left_enc_pos = 0L;
  else           right_enc_pos = 0L;
  SREG = sreg;
}

#else
  #error A encoder driver must be selected!
#endif

void resetEncoders() {
  resetEncoder(LEFT);
  resetEncoder(RIGHT);
}

#endif
