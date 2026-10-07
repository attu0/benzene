import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('benzene_ultrasonic')
    params_file = os.path.join(pkg_share, 'config', 'ultrasonic.yaml')

    use_sim = LaunchConfiguration('use_sim')
    use_sim_time = LaunchConfiguration('use_sim_time')

    hardware_node = Node(
        package='benzene_ultrasonic',
        executable='hcsr04',
        name='ultrasonic_hcsr04',
        output='screen',
        parameters=[params_file],
        condition=UnlessCondition(use_sim))

    sim_relay = Node(
        package='benzene_ultrasonic',
        executable='scan_to_range',
        name='ultrasonic_scan_to_range',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_sim))

    return LaunchDescription([
        DeclareLaunchArgument('use_sim', default_value='false',
                              description='true: relay Gazebo scan to Range; false: real HC-SR04'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        hardware_node,
        sim_relay,
    ])