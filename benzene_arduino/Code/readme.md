# Benzene Uno Firmware (PlatformIO)

Real-time base controller for the Benzene differential-drive robot.

The Arduino Uno handles wheel encoders, velocity PID control, and the L298N motor driver. The IMU and ultrasonic sensors are handled by the Raspberry Pi.

## Features

- Quadrature encoder decoding for both wheels
- Closed-loop wheel velocity control using PID
- L298N motor driver control
- Binary serial protocol with CRC8
- Typed serial commands for testing and debugging
- 50 Hz control loop
- Watchdog timeout to stop the motors when commands are no longer received

## Project Structure

| File | Purpose | Modify when |
|---|---|---|
| `include/config.h` | Pin assignments, direction signs, PID defaults, and timing | Rewiring, changing motor direction, or tuning PID |
| `src/encoders.cpp` | Quadrature decoding using two pin-change interrupt service routines | Changing encoder pins or decoding logic |
| `src/motors.cpp` | L298N PWM and direction control | Changing the motor driver |
| `src/pid.cpp` | Per-wheel velocity controller | Changing the control algorithm |
| `src/protocol.cpp` | Binary framing, CRC8, text-line parsing, and STATE messages | Adding or modifying protocol messages |
| `src/console.cpp` | Typed serial commands | Adding a diagnostic or test command |
| `src/main.cpp` | Main program, 50 Hz control loop, and watchdog | Adding new firmware behaviour |

The wire protocol is documented at the top of `include/protocol.h`.

## Requirements

- Arduino Uno
- L298N motor driver
- Two DC motors with quadrature encoders
- USB connection between the Uno and host computer
- PlatformIO Core or the PlatformIO extension for VS Code
- Python and `pyserial` for hardware bring-up tests

## Build and Upload

Run these commands from the firmware directory containing `platformio.ini`:

```bash
pio run
pio run --target upload
```

If multiple serial devices are connected, configure the correct upload port in the PlatformIO configuration before uploading.

## Wiring

### Wheel encoders

| Signal | Uno pin |
|---|---|
| Left encoder A | D2 |
| Left encoder B | D3 |
| Right encoder A | A4 |
| Right encoder B | A5 |
| Encoder VCC | 5V |
| Encoder GND | GND |

### L298N motor driver

| Signal | Uno pin |
|---|---|
| Left motor IN forward | D10 |
| Left motor IN backward | D6 |
| Left motor EN | D13 |
| Right motor IN forward | D9 |
| Right motor IN backward | D5 |
| Right motor EN | D12 |

The two EN pins are held HIGH. Motor outputs are not driven until the first non-zero motor command.

**Power and safety notes:**

- The Uno is powered over USB.
- Connect the battery negative, L298N GND, and Uno GND together.
- Keep the wheels off the ground during initial testing.
- Verify the actual pin assignments in `include/config.h` before wiring. If using an alternative wiring diagram, follow the configuration defined in the firmware.

## Testing and Bring-Up

The `tools/benzene_test.py` script is the hardware bring-up tool.

Install its Python dependency:

```bash
python3 -m pip install pyserial
```

Run the script's built-in help to check the supported command syntax:

```bash
python3 tools/benzene_test.py --help
```

The bring-up sequence is:

1. `listen` — check serial communication.
2. `ticks` — verify encoder tick reporting.
3. `cpr` — check counts per revolution.
4. `spin` — verify wheel direction and encoder signs.
5. `step` — test velocity response.
6. `watchdog` — verify the timeout behaviour.

Run tests with the wheels off the ground. The test tool aborts and stops the motors if an encoder sign is incorrect.

## Typed Serial Commands

The firmware supports one typed command per line. The `?` command lists available commands.

| Command | Purpose | Reply |
|---|---|---|
| `e` | Read encoder ticks | `left right` |
| `v` | Read measured wheel speeds in ticks/s | `left right` |
| `r` | Reset encoder counters | `OK` |
| `d <w> <c>` | Read a raw encoder pin (`w`: 0 = left, 1 = right; `c`: 0 = C1, 1 = C2) | `0` or `1` |
| `m <l> <r>` | Set closed-loop speed targets in ticks/s | `OK` |
| `o <l> <r>` | Set open-loop PWM from -255 to 255; bypasses PID | `OK` |
| `u kp ki kd [kff]` | Set PID gains | `OK` |

### Safety behaviour

- Motors stop two seconds after the last `m` or `o` command.
- The binary STATE stream remains disabled until the firmware receives its first binary frame.
- Sending a typed text command disables the binary STATE stream again, keeping serial-monitor output readable.

**Serial monitor note:** Do not use `pio device monitor` while another program owns the serial port. Only one program can use the port at a time. Close the monitor before running the Python bring-up tool or another serial client.

## Adding a New Protocol Message

1. Add the message type constant and callback declaration in `include/protocol.h`.
2. Implement message parsing and dispatch in `src/protocol.cpp`.
3. Connect the callback in `src/main.cpp`.
4. Update the protocol documentation and test the new message with the host software.

## Troubleshooting

| Problem | What to check |
|---|---|
| Upload fails | USB connection, selected upload port, and PlatformIO configuration |
| No encoder ticks | Encoder power, common ground, signal wiring, and pin assignments |
| Wheel moves in the wrong direction | Motor wiring and direction signs in `include/config.h` |
| Encoder counts decrease unexpectedly | Encoder A/B wiring and encoder direction configuration |
| Motors stop unexpectedly | Host command frequency and the two-second watchdog timeout |
| Serial port is busy | Close other serial clients before running tests |
| PID response is poor | Verify encoder scaling and tune PID parameters carefully |

## Related Packages

- `benzene_serial` — host-side serial communication.
- `benzene_hardware` — hardware integration with ROS 2 control.
- `benzene_control` — robot motion control.

Refer to the main [Benzene README](../README.md) for workspace-level setup and integration instructions.

## License

See the repository's [LICENSE](../LICENSE) file.
