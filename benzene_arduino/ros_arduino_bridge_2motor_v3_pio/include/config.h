#ifndef CONFIG_H
#define CONFIG_H

/* Enable the base controller (motors + encoders + PID) */
#define USE_BASE

#ifdef USE_BASE
  /* Encoders wired directly to the Arduino:
     D2/D3 (PORTD) and A4/A5 (PORTC), read with pin-change interrupts. */
  #define ARDUINO_ENC_COUNTER

  /* L298N wired as: EN pin = PWM, two direction pins = digital.
     (Your wiring. Upstream's L298 variant is different: PWM on IN pins.) */
  #define L298N_EN_PWM_DRIVER
#endif

/* Serial port baud rate (upstream default) */
#define BAUDRATE       57600

/* Maximum PWM signal */
#define MAX_PWM        255

/* Run the PID loop at 30 times per second */
#define PID_RATE       30     // Hz

/* Stop the robot if it hasn't received a movement command
   in this number of milliseconds */
#define AUTO_STOP_INTERVAL 2000

/* Encoder direction. 0 = same counting sign as the V3 code.
   Set to 1 to flip a wheel's count. Both wheels must COUNT UP when
   driven with positive PWM, otherwise the PID runs away (see README). */
#define LEFT_ENC_INVERT   0
#define RIGHT_ENC_INVERT  0

#endif
