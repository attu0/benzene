#!/usr/bin/env python3
"""Keyboard teleop for the benzene robot (sim and real)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[('/cmd_vel_in', '/cmd_vel_keyboard'),
                    ('/cmd_vel_out', '/diff_drive_controller/cmd_vel')]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),
        twist_stamper
    ])