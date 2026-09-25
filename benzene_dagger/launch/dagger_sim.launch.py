#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch the DAgger simulation environment with the Benzene robot in Gazebo.
    """

    # Get Benzene Gazebo package
    benzene_gz_dir = get_package_share_directory(
        'benzene_gazebo'
    )

    # Get Benzene description package
    benzene_description_dir = get_package_share_directory(
        'benzene_description'
    )

    # Resource path required by Gazebo
    # Example:
    # ~/ros2_ws/install/benzene_description/share/
    benzene_description_share = os.path.dirname(
        benzene_description_dir
    )

    # Existing Benzene Gazebo launch file
    benzene_gz_launch_file = os.path.join(
        benzene_gz_dir,
        'launch',
        'benzene.gazebo.launch.py'
    )

    benzene_dagger_dir = get_package_share_directory(
        'benzene_dagger'
    )

    rviz_config_file = os.path.join(
        benzene_dagger_dir  ,
        'rviz',
        'dagger.rviz'
    )

    scan_marker_cmd = Node(
        package='benzene_dagger',
        executable='scan_marker',
        name='lidar_visualizer_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([

        # Make Benzene description resources available to Gazebo
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=benzene_description_share
        ),
        scan_marker_cmd,

        # Launch the existing Benzene Gazebo simulation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                benzene_gz_launch_file
            ),
            launch_arguments={
                'world_file': 'race2.sdf',
                'robot_name': 'benzene',
                'use_sim_time': 'true',
                'use_rviz': 'true',
                'rviz_config_file': rviz_config_file,
                'load_controllers': 'true',
                'use_robot_state_pub': 'true',
                'launch_ekf': 'true',
                'enable_odom_tf': 'false',   # <-- add this
                'x': '-5.4',
                'y': '0.0',
                'z': '0.05',
                'roll': '0.0',
                'pitch': '0.0',
                'yaw': '-1.57',
            }.items()
        )
    ])