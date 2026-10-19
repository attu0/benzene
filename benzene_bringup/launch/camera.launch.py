#!/usr/bin/env python3
"""Pi Camera Module 3 publishing the same topics/frame as the sim cam_1."""

import os

from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

LIBCAMERA_LIB = '/usr/local/lib/aarch64-linux-gnu'


def generate_launch_description():
    existing = os.environ.get('LD_LIBRARY_PATH', '')
    ld_path = LIBCAMERA_LIB + (':' + existing if existing else '')

    return LaunchDescription([
        SetEnvironmentVariable('LD_LIBRARY_PATH', ld_path),
        Node(
            package='benzene_camera',
            executable='camera_node',
            name='cam_1',
            output='screen',
            remappings=[
                ('~/image_raw', '/cam_1/color/image_raw'),
                ('~/camera_info', '/cam_1/color/camera_info'),
            ],
            parameters=[{
                'camera': 0,
                'width': 640,
                'height': 480,
                'format': 'BGR888',   # should publish rgb8; verify below
                'camera_frame_id': 'cam_1_optical',
                'orientation': 180,
                # 'camera_info_url': 'file:///home/<you>/cam_1.yaml',  # after calibration
            }],
        ),
    ])