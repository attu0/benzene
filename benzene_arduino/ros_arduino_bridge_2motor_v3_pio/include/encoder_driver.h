/* *************************************************************
   Encoder driver function definitions - by James Nugen
   (upstream interface; pin mapping adapted to this robot)
   ************************************************************ */

#ifndef ENCODER_DRIVER_H
#define ENCODER_DRIVER_H

#include "config.h"

#ifdef ARDUINO_ENC_COUNTER
  /* Encoder connector mapping established during V3 testing:

       Connector D2/D3 (PORTD)  ->  measures the physical RIGHT motor
       Connector A4/A5 (PORTC)  ->  measures the physical LEFT  motor

     V3 called these connectors "LEFT encoder" and "RIGHT encoder" by
     connector name. From V4 on, LEFT / RIGHT mean the PHYSICAL WHEEL,
     so that `e` returns "<left wheel> <right wheel>" as ROS expects.
     That means the connector names are swapped relative to V3. */

  // Physical RIGHT wheel -> D2/D3 (PORTD)
  #define RIGHT_ENC_PIN_A PD2   // pin 2
  #define RIGHT_ENC_PIN_B PD3   // pin 3

  // Physical LEFT wheel -> A4/A5 (PORTC)
  #define LEFT_ENC_PIN_A  PC4   // pin A4
  #define LEFT_ENC_PIN_B  PC5   // pin A5

  /* Calibration measured on the robot (ticks per output-shaft rev),
     as reported by the V3 `e` command, listed BY CONNECTOR:
       A4/A5 connector: 23388 / 15 rev, 46814 / 30 rev -> 1559.83 ticks/rev
       D2/D3 connector: 23356 / 15 rev, 46762 / 30 rev -> 1557.89 ticks/rev
     The firmware only reports raw counts; use these values on the host. */
#endif

void initEncoders();
long readEncoder(int i);
void resetEncoder(int i);
void resetEncoders();

#endif
