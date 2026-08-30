#!/usr/bin/env python3
"""Bring up the real (non-Gazebo) benzene robot: RSP + controller_manager + controllers."""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share_description = FindPackageShare('benzene_description')
    pkg_share_bringup = FindPackageShare('benzene_bringup')

    urdf_model = PathJoinSubstitution(
        [pkg_share_description, 'urdf', 'robots', 'benzene.urdf.xacro'])

    robot_name = LaunchConfiguration('robot_name')
    prefix = LaunchConfiguration('prefix')

    declare_robot_name_cmd = DeclareLaunchArgument(
        'robot_name', default_value='benzene')
    declare_prefix_cmd = DeclareLaunchArgument(
        'prefix', default_value='')

    robot_description_content = ParameterValue(Command([
        'xacro', ' ', urdf_model, ' ',
        'robot_name:=', robot_name, ' ',
        'prefix:=', prefix, ' ',
        'use_gazebo:=false'
    ]), value_type=str)

    controllers_yaml = PathJoinSubstitution([
        pkg_share_description, 'config', robot_name, 'ros2_controllers.yaml'])

    # RSP (also generates ros2_controllers.yaml from the template)
    start_rsp_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                pkg_share_description.perform.__self__.find('benzene_description')
                if False else '', '')
        ]) if False else PythonLaunchDescriptionSource([
            PathJoinSubstitution(
                [pkg_share_description, 'launch', 'robot_state_publisher.launch.py'])
        ]),
        launch_arguments={
            'robot_name': robot_name,
            'prefix': prefix,
            'use_gazebo': 'false',
            'use_sim_time': 'false',
            'use_rviz': 'false',
        }.items()
    )

    # Real controller_manager — nothing auto-starts this outside Gazebo
    start_controller_manager_cmd = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description_content},
            controllers_yaml,
        ],
        output='screen',
    )

    # Give ros2_control_node time to open the serial port and come up
    # before the existing loader tries to talk to it
    load_controllers_cmd = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution(
                        [pkg_share_bringup, 'launch', 'load_ros2_controllers.launch.py'])
                ])
            )
        ]
    )

    ld = LaunchDescription()
    ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_prefix_cmd)
    ld.add_action(start_rsp_cmd)
    ld.add_action(start_controller_manager_cmd)
    ld.add_action(load_controllers_cmd)
    return ld