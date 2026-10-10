#!/usr/bin/env python3
"""
Launch SLAM + Nav2 for the REAL (non-Gazebo) benzene robot.

Run this on the LAPTOP. The Raspberry Pi must already be running

    ros2 launch benzene_bringup benzene_robot.launch.py include_rplidar:=true

because that publishes /scan, /tf, /tf_static, /robot_description and the
wheel odometry (/diff_drive_controller/odom, with enable_odom_tf: true).

What this launch file does:
  1. Builds the Nav2 parameter file at launch time:
       benzene_navigation/config/benzene_nav2_default_params.yaml  (your tuned sim params)
       +  benzene_real_nav2_overrides.yaml  (what differs on the real robot)
     Tune the real robot in the overrides file, not in the generated file.
  2. Starts nav2_bringup (slam:=True -> SLAM Toolbox, slam:=False -> AMCL
     on a saved map).
  3. Bridges Nav2's /cmd_vel (Twist) to /diff_drive_controller/cmd_vel
     (TwistStamped) with twist_stamper.
  4. Opens RViz.

Usage:
  Mapping:       ros2 launch benzene_bringup benzene_real_navigation.launch.py slam:=True
  Navigation:    ros2 launch benzene_bringup benzene_real_navigation.launch.py \
                     slam:=False map:=/path/to/map.yaml
"""

import copy
import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# The merged Nav2 parameter file is written here on every launch.
GENERATED_PARAMS = '/tmp/benzene_real_nav2_params.yaml'


def _deep_merge(base, over):
    """Merge dict `over` into dict `base` (in place) and return `base`.

    Nested dicts are merged key by key. Lists and scalars are replaced.
    A dict in `over` that contains `__replace__: true` replaces the whole
    dict in `base` instead of being merged into it.
    """
    for key, value in over.items():
        if isinstance(value, dict) and value.get('__replace__'):
            base[key] = {k: copy.deepcopy(v) for k, v in value.items()
                         if k != '__replace__'}
        elif isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base


def _launch_setup(context, *args, **kwargs):
    slam = LaunchConfiguration('slam').perform(context)
    map_yaml = LaunchConfiguration('map').perform(context)
    base_params_file = LaunchConfiguration('base_params_file').perform(context)
    overrides_file = LaunchConfiguration('overrides_file').perform(context)
    use_composition = LaunchConfiguration('use_composition').perform(context)
    odom_topic = LaunchConfiguration('odom_topic').perform(context)

    # 1. Build the Nav2 parameter file: installed defaults + our overrides.
    with open(base_params_file, 'r') as f:
        params = yaml.safe_load(f) or {}
    with open(overrides_file, 'r') as f:
        overrides = yaml.safe_load(f) or {}
    _deep_merge(params, overrides)
    # One place to choose the odometry source for every Nav2 node that reads it.
    for node_name in ('bt_navigator', 'controller_server', 'velocity_smoother'):
        params.setdefault(node_name, {}).setdefault('ros__parameters', {})[
            'odom_topic'] = odom_topic
    with open(GENERATED_PARAMS, 'w') as f:
        yaml.safe_dump(params, f, sort_keys=False, default_flow_style=False)

    # 2. SLAM Toolbox (slam:=True) or AMCL + map server (slam:=False) + Nav2.
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    start_nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'namespace': '',
            'use_namespace': 'false',
            'slam': slam,
            'map': map_yaml,
            'use_sim_time': 'false',
            'params_file': GENERATED_PARAMS,
            'autostart': 'true',
            'use_composition': use_composition,
            'use_respawn': 'false',
        }.items()
    )

    # 3. Nav2 publishes geometry_msgs/Twist on /cmd_vel; the real
    #    diff_drive_controller wants TwistStamped.
    #    The stamp comes from THIS machine's clock. Keep both machines
    #    NTP-synced, or run this node on the Pi instead (cmd_vel_bridge:=false).
    start_cmd_vel_bridge_cmd = Node(
        package='twist_stamper',
        executable='twist_stamper',
        name='nav_cmd_vel_stamper',
        output='screen',
        parameters=[{'use_sim_time': False}],
        remappings=[('cmd_vel_in', '/cmd_vel'),
                    ('cmd_vel_out', '/diff_drive_controller/cmd_vel')],
        condition=IfCondition(LaunchConfiguration('cmd_vel_bridge')),
    )

    # 4. RViz
    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config_file')],
        parameters=[{'use_sim_time': False}],
        output='log',
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    return [start_nav2_cmd, start_cmd_vel_bridge_cmd, start_rviz_cmd]


def generate_launch_description():
    pkg_share_navigation = get_package_share_directory('benzene_navigation')

    default_base_params = os.path.join(
        pkg_share_navigation, 'config', 'benzene_nav2_default_params.yaml')
    default_overrides = os.path.join(
        pkg_share_navigation, 'config', 'benzene_real_nav2_overrides.yaml')
    default_rviz = os.path.join(pkg_share_navigation, 'rviz', 'nav2_default_view.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'slam', default_value='True',
            description='True: build a map with SLAM Toolbox. False: localize with AMCL on `map`.'),
        DeclareLaunchArgument(
            'map', default_value='',
            description='Full path to the map .yaml (only used when slam:=False).'),
        DeclareLaunchArgument(
            'use_rviz', default_value='true',
            description='Open RViz.'),
        DeclareLaunchArgument(
            'use_composition', default_value='True',
            description='Run the Nav2 nodes in one composed container.'),
        DeclareLaunchArgument(
            'cmd_vel_bridge', default_value='true',
            description='Start twist_stamper (/cmd_vel -> /diff_drive_controller/cmd_vel).'),
        DeclareLaunchArgument(
            'base_params_file', default_value=default_base_params,
            description='Nav2 parameter file used as the base (your tuned sim params).'),
        DeclareLaunchArgument(
            'odom_topic', default_value='/diff_drive_controller/odom',
            description='Odometry topic for Nav2. Use /odometry/filtered once an EKF runs on the real robot.'),
        DeclareLaunchArgument(
            'overrides_file', default_value=default_overrides,
            description='Real-robot overrides merged on top of the base parameters.'),
        DeclareLaunchArgument(
            'rviz_config_file', default_value=default_rviz,
            description='RViz configuration file.'),
        OpaqueFunction(function=_launch_setup),
    ])