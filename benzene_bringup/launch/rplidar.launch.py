#!/usr/bin/env python3
"""Launch the RPLIDAR driver on the real robot.

The A1M8 can be left scanning (or half-initialised) after a driver crash or an
unclean shutdown. Every following start then fails with RESULT_OPERATION_TIMEOUT,
'80008000' (invalid data) or a health-code error until the lidar is power-cycled.

So:
  1. Before every driver start, send the lidar a STOP and a RESET command over
     its serial port (a software power-cycle, about 2 s).
  2. If the driver still exits with an error, reset the lidar again and start
     the driver again, up to MAX_ATTEMPTS times.

Needs pyserial:  sudo apt install python3-serial
"""

import time

from launch import LaunchDescription
from launch.actions import LogInfo, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

LIDAR_PORT = '/dev/benzene_rplidar'
LIDAR_BAUD = 115200
MAX_ATTEMPTS = 5

# Exit codes that mean "stopped on purpose" (clean exit, SIGINT, SIGTERM): never retry.
# A failed start shows up as 1 (scan mode failure) or -11 (driver segfault).
_INTENTIONAL_EXIT_CODES = (0, -2, -15)


def _reset_lidar(context, *args, **kwargs):
    """Send STOP + RESET to the lidar so the driver starts from a clean state.

    Blocks the launch process for about 2 s. Never raises: if the reset cannot
    be done, it logs why and lets the driver start anyway.
    """
    try:
        import serial  # provided by python3-serial
    except ImportError:
        return [LogInfo(msg='RPLIDAR reset skipped: pyserial is not installed '
                            '(sudo apt install python3-serial)')]

    try:
        with serial.Serial(LIDAR_PORT, LIDAR_BAUD, timeout=1) as s:
            s.write(b'\xA5\x25')     # stop scanning
            time.sleep(0.1)
            s.write(b'\xA5\x40')     # reset the lidar core
            time.sleep(2.0)          # let it reboot
            s.reset_input_buffer()   # drop leftover scan bytes / boot banner
    except (serial.SerialException, OSError) as exc:
        return [LogInfo(msg=f'RPLIDAR reset failed ({exc}); starting the driver anyway')]

    return [LogInfo(msg='RPLIDAR reset done')]


def _start_lidar(attempt):
    """Return the actions for one attempt: reset the lidar, then start the driver.

    If the driver exits with an error, the exit handler chains the next attempt.
    A fresh Node is built for every attempt, because a launch action cannot be
    started a second time.
    """
    lidar_node = Node(
        package='rplidar_ros',
        executable='rplidar_composition',
        name='rplidar',
        output='screen',
        parameters=[{
            'serial_port': LIDAR_PORT,
            'serial_baudrate': LIDAR_BAUD,
            'frame_id': 'laser_frame',
            'angle_compensate': True,
            'scan_mode': 'Standard',
        }],
    )

    def _on_lidar_exit(event, context):
        if (getattr(context, 'is_shutdown', False)
                or event.returncode in _INTENTIONAL_EXIT_CODES):
            return []
        if attempt >= MAX_ATTEMPTS:
            return [LogInfo(
                msg=f'RPLIDAR driver failed {MAX_ATTEMPTS} times in a row '
                    f'(last exit code {event.returncode}); giving up. '
                    'Unplug and replug the lidar, then relaunch.')]
        return [
            LogInfo(msg=f'RPLIDAR driver exited with code {event.returncode}; '
                        f'resetting and retrying (attempt {attempt + 1} of {MAX_ATTEMPTS})'),
            *_start_lidar(attempt + 1),
        ]

    return [
        RegisterEventHandler(OnProcessExit(target_action=lidar_node,
                                           on_exit=_on_lidar_exit)),
        OpaqueFunction(function=_reset_lidar),
        lidar_node,
    ]


def generate_launch_description():
    return LaunchDescription(_start_lidar(1))