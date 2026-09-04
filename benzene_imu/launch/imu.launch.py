#!/usr/bin/env python3
"""Launch the MPU6050 IMU driver, Madgwick filter, and EKF on the real robot."""

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    mpu6050_node = Node(
        package='benzene_imu',
        executable='mpu6050_publisher',
        name='mpu6050_publisher',
        output='screen',
        parameters=[{
            'i2c_bus': 1,
            'i2c_address': 0x68,
            'frame_id': 'imu_link',
            'publish_rate': 100.0,
            'calibration_samples': 400,
        }],
    )

    madgwick_node = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter_madgwick',
        output='screen',
        parameters=[{
            'use_mag': False,
            'publish_tf': False,
            'world_frame': 'enu',
            'use_sim_time': False,
            'gain': 0.1,
            'zeta': 0.0,
        }],
        remappings=[
            ('imu/data_raw', '/imu/data_raw'),
            ('imu/data', '/imu/data'),
        ],
    )

    return LaunchDescription([
        mpu6050_node,
        madgwick_node,
    ])