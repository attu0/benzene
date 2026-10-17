#!/usr/bin/env python3
"""Joystick teleop for the benzene robot (sim and real) - single file.

Matches teleop_keyboard: publishes geometry_msgs/TwistStamped on
/diff_drive_controller/cmd_vel with frame_id=base_link and a ZERO stamp,
so diff_drive_controller uses its own clock (no laptop/Pi clock-offset issues).

This file is both the launch file and the relay node: the launch description
starts this same script again with --relay to do the Twist -> TwistStamped step.
"""

import os
import sys

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


# ---------------------------------------------------------------------------
# Relay node (runs when this file is executed with --relay)
# ---------------------------------------------------------------------------
def run_relay(in_topic, out_topic, frame_id):
    import rclpy
    from rclpy.node import Node as RclNode
    from geometry_msgs.msg import Twist, TwistStamped

    class TwistZeroStampRelay(RclNode):
        def __init__(self):
            super().__init__('twist_zero_stamp_relay')
            self.pub = self.create_publisher(TwistStamped, out_topic, 10)
            self.sub = self.create_subscription(Twist, in_topic, self.cb, 10)

        def cb(self, twist):
            msg = TwistStamped()
            # Stamp intentionally left at zero so diff_drive_controller uses
            # its own clock and a clock offset can't reject commands.
            msg.header.frame_id = frame_id
            msg.twist = twist
            self.pub.publish(msg)

    rclpy.init()
    node = TwistZeroStampRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


# ---------------------------------------------------------------------------
# Launch description
# ---------------------------------------------------------------------------
def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    joy_params = os.path.join(
        get_package_share_directory('benzene_bringup'), 'config', 'joystick.yaml')

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[joy_params, {'use_sim_time': use_sim_time}],
    )

    # Publishes plain Twist on /cmd_vel_joy
    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_node',
        parameters=[joy_params, {'use_sim_time': use_sim_time}],
        remappings=[('/cmd_vel', '/cmd_vel_joy')]
    )

    # Replaces twist_stamper: this same file, run in relay mode
    twist_relay = ExecuteProcess(
        cmd=[sys.executable, os.path.abspath(__file__), '--relay',
             '/cmd_vel_joy', '/diff_drive_controller/cmd_vel', 'base_link'],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),
        joy_node,
        teleop_node,
        twist_relay,
    ])


if __name__ == '__main__':
    if len(sys.argv) >= 5 and sys.argv[1] == '--relay':
        run_relay(sys.argv[2], sys.argv[3], sys.argv[4])