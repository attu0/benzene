#!/usr/bin/env python3

"""Vision-based expert controller for the Benzene robot.

The expert no longer drives the robot. It only publishes its opinion on
/expert/cmd_vel (TwistStamped); dagger_mixer decides who actually drives.
"""

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float32


class ExpertController(Node):
    """Follow the yellow centerline using a PD controller."""

    def __init__(self):
        super().__init__('expert_controller')

        self.declare_parameter('linear_speed', 0.20)
        self.declare_parameter('kp', 0.65)
        self.declare_parameter('kd', 0.35)
        self.declare_parameter('max_angular_velocity', 0.8)
        # Change this if your camera resolution is different.
        self.declare_parameter('camera_width', 640.0)
        # ROS: +angular.z turns LEFT (counter-clockwise). A line to the RIGHT
        # of the image centre (positive error) needs a RIGHT turn (negative z),
        # so the PD output must be negated: steering_sign = -1.0.
        self.declare_parameter('steering_sign', -1.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value
        self.max_angular_velocity = self.get_parameter(
            'max_angular_velocity').value
        self.camera_width = float(self.get_parameter('camera_width').value)
        self.steering_sign = float(self.get_parameter('steering_sign').value)

        self.lateral_error = None
        self.heading_error = None
        self.last_line_time = None
        self.line_timeout = 0.5

        self.create_subscription(
            Float32, '/line/lateral_error', self.lateral_callback, 10)
        self.create_subscription(
            Float32, '/line/heading_error', self.heading_callback, 10)

        # Stamped label topic: the expert's action, used by
        # data_collector.py and by dagger_mixer.py.
        self.label_pub = self.create_publisher(
            TwistStamped, '/expert/cmd_vel', 10)

        self.create_timer(0.05, self.control_loop)

        self.get_logger().info('Benzene vision expert controller started.')
        self.get_logger().info(f'linear_speed = {self.linear_speed:.2f}')
        self.get_logger().info(f'Kp = {self.kp:.2f}, Kd = {self.kd:.2f}')
        self.get_logger().info(f'steering_sign = {self.steering_sign:+.1f}')

    def lateral_callback(self, msg):
        self.lateral_error = float(msg.data)
        self.last_line_time = self.get_clock().now()

    def heading_callback(self, msg):
        self.heading_error = float(msg.data)
        self.last_line_time = self.get_clock().now()

    def control_loop(self):
        """Compute and publish the expert label (never drives directly)."""

        # No label while the line is unknown or stale. The mixer stops
        # the robot if the expert is the active source, and the data
        # collector records nothing (no bogus zero labels).
        if self.lateral_error is None or self.heading_error is None:
            return

        age = (self.get_clock().now()
               - self.last_line_time).nanoseconds / 1e9
        if age > self.line_timeout:
            self.get_logger().warn(
                'Line detection timeout. No expert label published.',
                throttle_duration_sec=2.0)
            return

        normalized_lateral = self.lateral_error / (self.camera_width / 2.0)
        normalized_lateral = max(-1.0, min(1.0, normalized_lateral))

        angular_velocity = self.steering_sign * (
            self.kp * normalized_lateral
            + self.kd * self.heading_error
        )
        angular_velocity = max(
            -self.max_angular_velocity,
            min(self.max_angular_velocity, angular_velocity),
        )

        label = TwistStamped()
        label.header.stamp = self.get_clock().now().to_msg()
        label.header.frame_id = 'base_link'
        label.twist.linear.x = self.linear_speed
        label.twist.angular.z = angular_velocity

        self.label_pub.publish(label)


def main(args=None):
    rclpy.init(args=args)
    node = ExpertController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()