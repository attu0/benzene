#!/usr/bin/env python3
"""Launch the Pi Camera Module 3 (libcamera) driver on the real robot."""

import os

from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

LIBCAMERA_LIB = '/usr/local/lib/aarch64-linux-gnu'


def generate_launch_description():
    # Make sure camera_node loads the Raspberry Pi libcamera fork,
    # not any other libcamera on the system.
    ld_path = LIBCAMERA_LIB + ':' + os.environ.get('LD_LIBRARY_PATH', '')

    return LaunchDescription([
        SetEnvironmentVariable('LD_LIBRARY_PATH', ld_path),
        Node(
            package='benzene_camera',
            executable='camera_node',
            name='camera',
            output='screen',
            parameters=[{
                'camera': 0,
                'width': 640,
                'height': 480,
                'format': 'RGB888',
                'camera_frame_id': 'camera_optical',
                'orientation': 180,
            }],
        ),
    ])