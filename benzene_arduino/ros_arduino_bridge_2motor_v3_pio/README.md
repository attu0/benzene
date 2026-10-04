# ROS Arduino Bridge - 2 Motor V4 (PlatformIO)

V3 rebuilt to match the serial protocol of
[joshnewans/ros_arduino_bridge](https://github.com/joshnewans/ros_arduino_bridge)
(a fork of hbrobotics/ros_arduino_bridge), so ROS-side drivers that speak that
protocol work with this robot. Your hardware settings from V3 are kept.

```text
pio run                  build
pio run -t upload        build + flash
pio device monitor       serial monitor (57600, CR line ending - preset)
```

## Serial protocol (same as upstream)

57600 baud. **Every command ends with a carriage return (CR, `\r`)**.

```text
e                  read encoders           -> "<left> <right>"
r                  reset encoders + PID    -> OK
o <L> <R>          raw PWM, -255..255      -> OK   (PID off)
m <L> <R>          closed-loop speed, in encoder COUNTS PER FRAME -> OK
u <Kp>:<Kd>:<Ki>:<Ko>   set PID gains      -> OK
b                  print baud rate
a/d <pin>          analogRead / digitalRead
c/w/x <pin> <val>  pinMode / digitalWrite / analogWrite     -> OK
p <pin>            ping (ultrasonic distance, cm)
```

- A frame is 1/30 s (30 Hz PID). 1 rev/s is about 1558/30 = 52 counts/frame.
- **Auto-stop:** motors stop if no `o` / `m` arrives for 2 s. Keep sending.
- `m 0 0` stops and resets the PID.
- Default PID gains are upstream's (`20:12:0:50`), tuned for a different
  robot. Expect to tune them with `u`.

### Moving from the V3 commands

| V3 | V4 |
|---|---|
| `f 100` | `o 100 100` |
| `b 100` | `o -100 -100` |
| `l 100` | `o -100 100` |
| `t 100` | `o 100 -100` |
| `s` / `0` / `x` | `o 0 0` (or `m 0 0`) |
| `h` | removed |
| `e` | `e` (now one line: `<left> <right>`) |
| `r` | `r` (now prints `OK`) |

`s`, `t`, `b`, `x` could not be kept: upstream uses those letters
for servo write, servo read, baud rate and analogWrite.

## Direction (unchanged from V3)

Positive PWM = shaft **clockwise** on both motors.

```text
o 100 100     both clockwise            (forward)
o -100 -100   both counter-clockwise    (backward)
o -100 100    LEFT ccw, RIGHT cw        (turn left)
o 100 -100    LEFT cw,  RIGHT ccw       (turn right)
```

## Pins

| Function | Pins |
|---|---|
| Right motor | EN 5 (PWM), FORWARD 9, BACKWARD 8 |
| Left motor | EN 6 (PWM), FORWARD 10, BACKWARD 11 |
| Right wheel encoder | D2 / D3 |
| Left wheel encoder | A4 / A5 |

Both encoders are read in pin-change interrupts (PCINT2 for D2/D3, PCINT1 for
A4/A5). In V3 the A4/A5 encoder was polled in `loop()`.

**LEFT / RIGHT now mean the physical wheel.** In V3 the "LEFT encoder"
was the D2/D3 connector, which measures the physical RIGHT motor. V4 follows
the wheel, so `e` prints `<left wheel> <right wheel>` as ROS expects.

## First power-up (wheels OFF the ground)

A closed loop with the wrong encoder sign is positive feedback: the wheel
runs to full PWM. Check signs before using `m`.

1. `o 80 0` then `e` twice. The **first** number must change. (If the second
   one changes, the connector mapping is the other way round: swap the
   `LEFT_ENC_*` / `RIGHT_ENC_*` pin defines in `include/encoder_driver.h` and
   the matching ISR bodies.)
2. The number must **increase**. If it decreases, set `LEFT_ENC_INVERT 1` in
   `include/config.h`.
3. Repeat with `o 0 80` for the right wheel (second number,
   `RIGHT_ENC_INVERT`).
4. `o 0 0`, then try `m 10 10` (about 0.19 rev/s) and finish with `m 0 0`.

## Encoder calibration (from V3)

Measured by connector, as printed by the V3 `e` command:

| Connector | 15 rev | 30 rev | Average |
|---|---:|---:|---:|
| A4 / A5 (left wheel) | 23388 | 46814 | 1559.83 ticks/rev |
| D2 / D3 (right wheel) | 23356 | 46762 | 1557.89 ticks/rev |

The firmware reports raw counts only. Put ticks/rev in the host-side
configuration (e.g. your ROS driver). Please double-check which connector each
number belongs to; V3 labelled them "RIGHT" and "LEFT" by connector name.

## Layout

```text
include/config.h           build options, baud, PID rate, encoder invert
include/commands.h         command letters
include/motor_driver.h     pins (your L298N wiring)
include/encoder_driver.h   pins + notes
include/diff_controller.h  PID (upstream, unchanged)
include/sensors.h          ping
src/main.cpp               command parser + main loop
src/motor_driver.cpp
src/encoder_driver.cpp
```

Not ported: upstream's servo module (its default pins 3/4 collide with your
D3 encoder input, and the robot has no servos).

## Credits / license

Protocol, PID and command parser: Patrick Goebel / James Nugen (HBRC) and
Josh Newans, BSD license. The notice is kept at the top of `src/main.cpp`.