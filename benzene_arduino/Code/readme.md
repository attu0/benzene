# benzene Uno firmware (PlatformIO)

Real-time base controller for the benzene diff-drive robot. The Uno only does
encoders, velocity PID and the L298N; IMU and ultrasonic live on the Pi.

| File | Job | Touch it when... |
|---|---|---|
| `include/config.h` | pins, signs, PID defaults, timing | rewiring, flipping a direction, retuning |
| `src/encoders.cpp` | 4x quadrature decode (one ISR) | encoder pins or decoding change |
| `src/motors.cpp` | L298N PWM + direction | swapping the motor driver |
| `src/pid.cpp` | per-wheel velocity controller | changing the control law |
| `src/protocol.cpp` | framing, CRC8, parser, STATE message | adding/changing messages |
| `src/main.cpp` | glue + 50 Hz loop + watchdog | adding new behaviour |

The wire protocol is documented at the top of `include/protocol.h`.
Don't use `pio device monitor`: the link is binary and one program owns the port.

Adding a new message: add a type constant + callback in `protocol.h`, parse it
in `dispatch()` in `protocol.cpp`, and wire the callback in `main.cpp`.