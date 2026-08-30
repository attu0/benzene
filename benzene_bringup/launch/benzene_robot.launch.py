#!/usr/bin/env python3
"""
Bring up the real (non-Gazebo) benzene robot.

This launch file sets up the physical robot: robot state publisher, the
ros2_control controller_manager talking to the Arduino over serial via
benzene_hardware, the diff drive + joint state broadcaster controllers,
and (optionally) the RPLIDAR and camera drivers.
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Generate a launch description for the real robot.

    Returns:
        LaunchDescription: A complete launch description for the physical robot
    """
    # Constants for paths to different packages
    package_name_bringup = 'benzene_bringup'
    package_name_description = 'benzene_description'

    default_robot_name = 'benzene'
    urdf_filename = 'benzene.urdf.xacro'

    # Set the path to different packages
    pkg_share_bringup = FindPackageShare(package=package_name_bringup).find(package_name_bringup)
    pkg_share_description = FindPackageShare(
        package=package_name_description).find(package_name_description)

    default_urdf_model_path = PathJoinSubstitution(
        [pkg_share_description, 'urdf', 'robots', urdf_filename])

    # Launch configuration variables
    include_camera = LaunchConfiguration('include_camera')
    include_rplidar = LaunchConfiguration('include_rplidar')
    jsp_gui = LaunchConfiguration('jsp_gui')
    prefix = LaunchConfiguration('prefix')
    robot_name = LaunchConfiguration('robot_name')
    use_rviz = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Declare the launch arguments
    declare_include_camera_cmd = DeclareLaunchArgument(
        name='include_camera',
        default_value='True',
        description='Whether to launch the camera driver')

    declare_include_rplidar_cmd = DeclareLaunchArgument(
        name='include_rplidar',
        default_value='True',
        description='Whether to launch the RPLIDAR driver')

    declare_jsp_gui_cmd = DeclareLaunchArgument(
        name='jsp_gui',
        default_value='false',
        description='Flag to enable joint_state_publisher_gui '
                     '(never enable this on the real robot — it will '
                     'fight the real joint_state_broadcaster for /joint_states)')

    declare_prefix_cmd = DeclareLaunchArgument(
        name='prefix',
        default_value='',
        description='Prefix for robot joints and links')

    declare_robot_name_cmd = DeclareLaunchArgument(
        name='robot_name',
        default_value=default_robot_name,
        description='The name for the robot')

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='false',
        description='Flag to enable RViz')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='false',
        choices=['true', 'false'],
        description='Use simulation clock if true — should stay false on the real robot')

    # robot_description, generated directly via xacro for the controller_manager
    robot_description_content = ParameterValue(Command([
        'xacro', ' ', default_urdf_model_path, ' ',
        'robot_name:=', robot_name, ' ',
        'prefix:=', prefix, ' ',
        'use_gazebo:=false'
    ]), value_type=str)

    controllers_yaml = PathJoinSubstitution([
        pkg_share_description, 'config', robot_name, 'ros2_controllers.yaml'])

    # Include Robot State Publisher launch file
    # (also generates ros2_controllers.yaml from the template)
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_share_description, 'launch', 'robot_state_publisher.launch.py')
        ]),
        launch_arguments={
            'robot_name': robot_name,
            'prefix': prefix,
            'use_gazebo': 'false',
            'use_sim_time': use_sim_time,
            'use_rviz': use_rviz,
            'jsp_gui': jsp_gui,
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

    # spawner retries against controller_manager on its own — no fixed
    # delay to guess, unlike a raw ExecuteProcess/load_controller approach
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
    )

    # Start diff_drive_controller only once joint_state_broadcaster has
    # finished spawning
    delay_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner = (
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_controller_spawner],
            )
        )
    )

    # Include RPLIDAR launch file if enabled
    include_rplidar_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_share_bringup, 'launch', 'rplidar.launch.py')
        ]),
        condition=IfCondition(include_rplidar)
    )

    # Include camera launch file if enabled
    include_camera_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_share_bringup, 'launch', 'camera.launch.py')
        ]),
        condition=IfCondition(include_camera)
    )

    # Defer sensors launch to avoid overhead while robot_state_publisher
    # and controller_manager are setting up
    rplidar_timer = TimerAction(period=3.0, actions=[include_rplidar_cmd])
    camera_timer = TimerAction(period=3.0, actions=[include_camera_cmd])

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_include_camera_cmd)
    ld.add_action(declare_include_rplidar_cmd)
    ld.add_action(declare_jsp_gui_cmd)
    ld.add_action(declare_prefix_cmd)
    ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_use_sim_time_cmd)

    # Add the actions to the launch description
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(start_controller_manager_cmd)
    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(delay_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner)
    ld.add_action(rplidar_timer)
    ld.add_action(camera_timer)

    return ld