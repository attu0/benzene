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

## Wiring (same pins as the ros_arduino_bridge reference)

| Signal | Uno pin |
|---|---|
| Left encoder A / B | D2 / D3 |
| Right encoder A / B | A4 / A5 |
| Left motor: IN fwd / IN back / EN | D10 / D6 / D13 |
| Right motor: IN fwd / IN back / EN | D9 / D5 / D12 |
| Encoder VCC / GND | 5V / GND |

The IN pins get the PWM; the two EN pins are held HIGH. Motor pins are not touched
until the first non-zero motor command. Common ground: battery -, L298N GND, Uno GND.
The Uno is powered over USB. (Using the first diagram's pins instead: see `config.h`.)

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