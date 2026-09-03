#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import time
import math


class SquareController(Node):

    def __init__(self):
        super().__init__('square_controller')

        self.publisher = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        # Parameters
        self.linear_speed = 0.2      # m/s
        self.angular_speed = 0.5     # rad/s
        self.side_length = 1.0       # meters

        # Calculate movement times
        self.forward_time = (
            self.side_length / self.linear_speed
        )

        self.turn_time = (
            (math.pi / 2) / self.angular_speed
        )

        self.get_logger().info(
            'Starting square movement'
        )

        self.move_square()

    def publish_velocity(self, linear_x=0.0, angular_z=0.0):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        msg.twist.linear.x = linear_x
        msg.twist.angular.z = angular_z

        self.publisher.publish(msg)

    def move_for_time(self, linear_x, angular_z, duration):

        start_time = time.time()

        while time.time() - start_time < duration:

            self.publish_velocity(
                linear_x,
                angular_z
            )

            time.sleep(0.05)

        self.stop_robot()
        time.sleep(0.5)

    def stop_robot(self):

        self.publish_velocity(0.0, 0.0)

    def move_square(self):

        for side in range(4):

            self.get_logger().info(
                f'Moving side {side + 1}'
            )

            # Move forward
            self.move_for_time(
                self.linear_speed,
                0.0,
                self.forward_time
            )

            self.get_logger().info(
                'Turning 90 degrees'
            )

            # Turn left 90 degrees
            self.move_for_time(
                0.0,
                self.angular_speed,
                self.turn_time
            )

        self.stop_robot()

        self.get_logger().info(
            'Square completed!'
        )


def main(args=None):

    rclpy.init(args=args)

    node = SquareController()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()