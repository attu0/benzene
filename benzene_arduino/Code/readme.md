# benzene Uno firmware (PlatformIO)

Real-time base controller for the benzene diff-drive robot. The Uno only does
encoders, velocity PID and the L298N; IMU and ultrasonic live on the Pi.

| File | Job | Touch it when... |
|---|---|---|
| `include/config.h` | pins, signs, PID defaults, timing | rewiring, flipping a direction, retuning |
| `src/encoders.cpp` | 4x quadrature decode (two pin-change ISRs) | encoder pins or decoding change |
| `src/motors.cpp` | L298N PWM + direction | swapping the motor driver |
| `src/pid.cpp` | per-wheel velocity controller | changing the control law |
| `src/protocol.cpp` | binary framing, CRC8, text-line splitter, STATE message | adding/changing messages |
| `src/console.cpp` | typed serial commands (`e`, `m`, `o`, `u`, ...) | adding a typed test command |
| `src/main.cpp` | glue + 50 Hz loop + watchdog | adding new behaviour |

The wire protocol is documented at the top of `include/protocol.h`.
Don't use `pio device monitor`: the link is binary and one program owns the port.

Adding a new message: add a type constant + callback in `protocol.h`, parse it
in `dispatch()` in `protocol.cpp`, and wire the callback in `main.cpp`.

## Wiring (from the diagram)

| Signal | Uno pin |
|---|---|
| ENA (left PWM) | D5 |
| IN1 / IN2 (left dir) | D11 / D10 |
| IN3 / IN4 (right dir) | D8 / D9 |
| ENB (right PWM) | D6 |
| Left encoder C1 / C2 | A4 / A5 |
| Right encoder C1 / C2 | D3 / D2 |
| Encoder VCC / GND | 5V / GND |

Battery + -> L298N 12V terminal, battery - -> L298N GND and Uno GND (common ground).
The Uno is powered over USB from the Pi.

## Testing

`tools/benzene_test.py` (needs `pip install pyserial`) is the bring-up tool:
`listen` -> `ticks` -> `cpr` -> `spin` -> `step` -> `watchdog`. Run it with the
wheels off the ground. It aborts and stops the motors if an encoder sign is wrong.

## Typed serial commands (serial monitor)

`pio device monitor` works now. Type one command per line (`?` lists them):

| Command | Does | Reply |
|---|---|---|
| `e` | encoder ticks | `left right` |
| `v` | measured speed (ticks/s) | `left right` |
| `r` | reset encoders | `OK` |
| `d <w> <c>` | raw encoder pin (w 0=L 1=R, c 0=C1 1=C2) | `0` / `1` |
| `m <l> <r>` | closed-loop speed targets, ticks/s | `OK` |
| `o <l> <r>` | open-loop PWM -255..255 (bypasses PID) | `OK` |
| `u kp ki kd [kff]` | set PID gains | `OK` |

Motors stop 2 s after the last `m`/`o`. The binary STATE stream is off until a
binary host sends its first frame, and a typed line switches it off again, so the
monitor stays readable.