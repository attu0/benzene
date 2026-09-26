#!/usr/bin/env python3

"""
Launch the complete Benzene expert-data collection pipeline.

Starts:
    1. Benzene Gazebo simulation
    2. OpenCV yellow-line detector
    3. Vision-based expert controller
    4. Synchronized dataset collector
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    # ---------------------------------------------------------
    # Package directories
    # ---------------------------------------------------------

    benzene_dagger_dir = get_package_share_directory(
        'benzene_dagger'
    )

    # Existing simulation launch
    sim_launch = os.path.join(
        benzene_dagger_dir,
        'launch',
        'dagger_sim.launch.py'
    )

    # ---------------------------------------------------------
    # Benzene simulation
    # ---------------------------------------------------------

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch)
    )

    # ---------------------------------------------------------
    # OpenCV line detector
    # ---------------------------------------------------------

    line_detector = Node(
        package='benzene_dagger',
        executable='line_detector.py',
        name='yellow_line_detector',
        output='screen',
        parameters=[
            {
                'use_sim_time': True
            }
        ],
    )

    # ---------------------------------------------------------
    # Expert controller
    # ---------------------------------------------------------

    expert_controller = Node(
        package='benzene_dagger',
        executable='expert_controller.py',
        name='expert_controller',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'linear_speed': 0.20,
                'kp': 0.65,
                'kd': 0.35,
                'max_angular_velocity': 0.8,
            }
        ],
    )

    # ---------------------------------------------------------
    # Dataset collector
    # ---------------------------------------------------------

    data_collector = Node(
        package='benzene_dagger',
        executable='data_collector.py',
        name='data_collector',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,

                # Dataset location
                'dataset_dir':
                    os.path.expanduser(
                        '~/ros2_ws/src/benzene/benzene_dagger/dataset'
                    ),

                # Empty = automatically generate episode name
                'episode_name': '',

                # Image/action synchronization tolerance
                'sync_slop': 0.05,
            }
        ],
    )

    # ---------------------------------------------------------
    # Launch everything
    # ---------------------------------------------------------

    return LaunchDescription([

        # Start simulation first
        simulation,

        # Vision detector
        line_detector,

        # Expert controller
        expert_controller,

        # Dataset recorder
        data_collector,
    ])