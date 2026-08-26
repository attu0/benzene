/*
 * Author: Automatic Addison
 * Website: https://automaticaddison.com
 * Description: Count the number of encoder pulses per revolution.
 */

// Encoder output to Arduino Interrupt pin. Tracks the pulse count.


//https://automaticaddison.com/wp-content/uploads/2021/04/jgb37_dc_motor_with_encoder-1.jpg
#define ENC_IN_A 2

// Keep track of the number of wheel pulses
volatile long wheel_pulse_count = 0;

void setup() {

  // Open the serial port at 57600 bps
  Serial.begin(57600);

  // Set pin states of the encoder
  pinMode(ENC_IN_A , INPUT_PULLUP);

  // Every time the pin goes high, this is a pulse
  attachInterrupt(digitalPinToInterrupt(ENC_IN_A), wheel_pulse, RISING);

}

void loop() {

    Serial.print(" Pulses: ");
    Serial.println(wheel_pulse_count);
}

// Increment the number of pulses by 1
void wheel_pulse() {
  wheel_pulse_count++;
}