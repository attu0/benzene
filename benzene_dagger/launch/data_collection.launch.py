#!/usr/bin/env python3

"""
Launch the Benzene DAgger data-collection pipeline.

Starts:
    1. Benzene Gazebo simulation
    2. OpenCV yellow-line detector
    3. Expert controller (label only, /expert/cmd_vel)
    4. Learner controller (optional, /learner/cmd_vel)
    5. DAgger mixer (only node that drives the robot)
    6. Synchronized dataset collector

Examples:
    # Iteration 0: pure expert (behavioral cloning data)
    ros2 launch benzene_dagger data_collection.launch.py

    # DAgger iteration: learner drives 70%, expert drives 30%
    ros2 launch benzene_dagger data_collection.launch.py \
        use_learner:=true beta:=0.3
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    benzene_dagger_dir = get_package_share_directory('benzene_dagger')

    sim_launch = os.path.join(
        benzene_dagger_dir, 'launch', 'dagger_sim.launch.py')

    beta = LaunchConfiguration('beta')
    mix_hold_time = LaunchConfiguration('mix_hold_time')
    use_learner = LaunchConfiguration('use_learner')
    steering_sign = LaunchConfiguration('steering_sign')

    declare_args = [
        DeclareLaunchArgument(
            'beta', default_value='1.0',
            description='Probability the expert drives (1.0 = pure expert, '
                        '0.0 = pure learner).'),
        DeclareLaunchArgument(
            'mix_hold_time', default_value='1.0',
            description='Seconds between re-sampling expert/learner.'),
        DeclareLaunchArgument(
            'use_learner', default_value='false',
            description='Start the CNN learner controller.'),
        DeclareLaunchArgument(
            'steering_sign', default_value='-1.0',
            description='-1.0 steers toward the line (correct for ROS). '
                        'Use 1.0 only to reproduce the old, inverted expert.'),
    ]

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch))

    line_detector = Node(
        package='benzene_dagger',
        executable='line_detector.py',
        name='yellow_line_detector',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    expert_controller = Node(
        package='benzene_dagger',
        executable='expert_controller.py',
        name='expert_controller',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'linear_speed': 0.20,
            'kp': 0.65,
            'kd': 0.35,
            'max_angular_velocity': 0.8,
            'steering_sign': ParameterValue(steering_sign, value_type=float),
        }],
    )

    cnn_controller = Node(
        package='benzene_dagger',
        executable='cnn_controller.py',
        name='cnn_controller',
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(use_learner),
    )

    mixer = Node(
        package='benzene_dagger',
        executable='dagger_mixer.py',
        name='dagger_mixer',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'beta': ParameterValue(beta, value_type=float),
            'mix_hold_time': ParameterValue(mix_hold_time, value_type=float),
        }],
    )

    data_collector = Node(
        package='benzene_dagger',
        executable='data_collector.py',
        name='data_collector',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'dataset_dir': os.path.expanduser(
                '~/ros2_ws/src/benzene/benzene_dagger/dataset'),
            'episode_name': '',
            'sync_slop': 0.05,
        }],
    )

    return LaunchDescription([
        *declare_args,
        simulation,
        line_detector,
        expert_controller,
        cnn_controller,
        mixer,
        data_collector,
    ])