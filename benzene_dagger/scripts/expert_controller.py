#!/usr/bin/env python3

"""Vision-based expert controller for the Benzene robot."""

import time

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import Float32


class ExpertController(Node):
    """Follow the yellow centerline using a PD controller."""

    def __init__(self):
        super().__init__('expert_controller')

        # ---------------------------------------------------------
        # Controller parameters
        # ---------------------------------------------------------

        self.declare_parameter('linear_speed', 0.20)
        self.declare_parameter('kp', 0.65)
        self.declare_parameter('kd', 0.35)
        self.declare_parameter('max_angular_velocity', 0.8)

        self.linear_speed = self.get_parameter(
            'linear_speed'
        ).value

        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value

        self.max_angular_velocity = self.get_parameter(
            'max_angular_velocity'
        ).value

        # Camera width.
        # Change this if your camera resolution is different.
        self.camera_width = 640.0

        # ---------------------------------------------------------
        # State
        # ---------------------------------------------------------

        self.lateral_error = None
        self.heading_error = None

        self.last_time = time.time()
        self.last_command_time = time.time()

        self.line_timeout = 0.5

        # ---------------------------------------------------------
        # Subscribers
        # ---------------------------------------------------------

        self.lateral_sub = self.create_subscription(
            Float32,
            '/line/lateral_error',
            self.lateral_callback,
            10,
        )

        self.heading_sub = self.create_subscription(
            Float32,
            '/line/heading_error',
            self.heading_callback,
            10,
        )

        # ---------------------------------------------------------
        # Publishers
        # ---------------------------------------------------------

        self.cmd_pub = self.create_publisher(
            Twist,
            '/diff_drive_controller/cmd_vel',
            10,
        )

        # Stamped label topic, always the expert's action, used by
        # data_collector.py for image/action synchronization.
        self.label_pub = self.create_publisher(
            TwistStamped,
            '/expert/cmd_vel',
            10,
        )

        # ---------------------------------------------------------
        # Control timer
        # ---------------------------------------------------------

        self.timer = self.create_timer(
            0.05,
            self.control_loop,
        )

        self.get_logger().info(
            'Benzene vision expert controller started.'
        )

        self.get_logger().info(
            f'linear_speed = {self.linear_speed:.2f}'
        )

        self.get_logger().info(
            f'Kp = {self.kp:.2f}, Kd = {self.kd:.2f}'
        )

    def lateral_callback(self, msg):
        """Receive lateral error."""

        self.lateral_error = float(msg.data)
        self.last_command_time = time.time()

    def heading_callback(self, msg):
        """Receive heading error."""

        self.heading_error = float(msg.data)
        self.last_command_time = time.time()

    def control_loop(self):
        """Calculate and publish the expert driving command."""

        current_time = time.time()

        # ---------------------------------------------------------
        # Safety: stop if line detection is lost.
        # ---------------------------------------------------------

        if (
            self.lateral_error is None
            or self.heading_error is None
        ):
            self.stop_robot()
            return

        if (
            current_time - self.last_command_time
            > self.line_timeout
        ):
            self.get_logger().warn(
                'Line detection timeout. Stopping robot.'
            )
            self.stop_robot()
            return

        # ---------------------------------------------------------
        # Normalize lateral error.
        #
        # Example:
        #
        # -320 px -> -1.0
        #    0 px ->  0.0
        # +320 px -> +1.0
        # ---------------------------------------------------------

        normalized_lateral = (
            self.lateral_error
            / (self.camera_width / 2.0)
        )

        normalized_lateral = max(
            -1.0,
            min(1.0, normalized_lateral),
        )

        # ---------------------------------------------------------
        # Calculate steering command.
        # ---------------------------------------------------------

        angular_velocity = (
            self.kp * normalized_lateral
            + self.kd * self.heading_error
        )

        # ---------------------------------------------------------
        # Clamp steering.
        # ---------------------------------------------------------

        angular_velocity = max(
            -self.max_angular_velocity,
            min(
                self.max_angular_velocity,
                angular_velocity,
            ),
        )

        # ---------------------------------------------------------
        # Publish Twist.
        # ---------------------------------------------------------

        cmd = Twist()

        cmd.linear.x = self.linear_speed
        cmd.linear.y = 0.0
        cmd.linear.z = 0.0

        cmd.angular.x = 0.0
        cmd.angular.y = 0.0
        cmd.angular.z = angular_velocity

        self.cmd_pub.publish(cmd)

        # ---------------------------------------------------------
        # Publish stamped label (always the expert's opinion,
        # regardless of who is actually driving the robot).
        # ---------------------------------------------------------

        label_msg = TwistStamped()
        label_msg.header.stamp = self.get_clock().now().to_msg()
        label_msg.header.frame_id = 'base_link'
        label_msg.twist = cmd

        self.label_pub.publish(label_msg)

        self.last_time = current_time

    def stop_robot(self):
        """Stop the robot."""

        cmd = Twist()

        cmd.linear.x = 0.0
        cmd.linear.y = 0.0
        cmd.linear.z = 0.0

        cmd.angular.x = 0.0
        cmd.angular.y = 0.0
        cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)


def main(args=None):
    """Run the expert controller."""

    rclpy.init(args=args)

    node = ExpertController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()