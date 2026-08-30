#!/usr/bin/env python3
"""Launch the USB camera driver on the real robot."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            output='screen',
            parameters=[{
                'image_size': [640, 480],
                'camera_frame_id': 'camera_optical'
            }]
        )
    ])