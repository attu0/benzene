#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import math
from enum import Enum

class State(Enum):
    MOVING_FORWARD = 1
    U_TURN = 2
    RETURNING = 3
    FINISHED = 4

class OutAndBackController(Node):
    def __init__(self):
        super().__init__('out_and_back_controller')

        # Publisher and Subscriber using standard diff drive topics
        self.publisher = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            10
        )

        # 50ms control loop
        self.timer = self.create_timer(0.05, self.control_loop)

        # Robot State Variables
        self.state = State.MOVING_FORWARD
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        self.start_x = 0.0
        self.start_y = 0.0
        self.turn_start_yaw = 0.0

        self.got_odom = False
        self.initialized = False

        self.get_logger().info('Starting 1m forward, U-turn, and return sequence.')

    def euler_yaw_from_quaternion(self, q):
        """Convert quaternion to euler yaw angle."""
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def normalize_angle(self, angle):
        """Keep angle between -Pi and Pi."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def clamp(self, value, min_val, max_val):
        """Limit a value between a minimum and maximum."""
        # Ensure we maintain the sign (forward/reverse or left/right turn)
        sign = 1 if value >= 0 else -1
        abs_val = abs(value)
        clamped_abs = max(min_val, min(abs_val, max_val))
        return sign * clamped_abs

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_yaw = self.euler_yaw_from_quaternion(msg.pose.pose.orientation)
        self.got_odom = True

    def control_loop(self):
        if not self.got_odom:
            return

        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        if not self.initialized:
            self.start_x = self.current_x
            self.start_y = self.current_y
            self.initialized = True

        # -------------------------
        # 1. MOVE FORWARD 1 METER
        # -------------------------
        if self.state == State.MOVING_FORWARD:
            target_distance = 1.0
            distance_traveled = math.sqrt(
                (self.current_x - self.start_x)**2 +
                (self.current_y - self.start_y)**2
            )

            error = target_distance - distance_traveled

            if error <= 0.02:  # 2cm tolerance
                msg.twist.linear.x = 0.0
                self.turn_start_yaw = self.current_yaw
                self.state = State.U_TURN
                self.get_logger().info('Reached 1m. Starting U-Turn.')
            else:
                kp_linear = 0.5
                linear_cmd = self.clamp(kp_linear * error, 0.05, 0.2)
                msg.twist.linear.x = linear_cmd

        # -------------------------
        # 2. U-TURN (180 DEGREES / Pi RADIANS)
        # -------------------------
        elif self.state == State.U_TURN:
            target_angle = math.pi # 180 degrees
            angle_turned = abs(self.normalize_angle(self.current_yaw - self.turn_start_yaw))

            error = target_angle - angle_turned

            if error <= 0.02:  # ~1.1 degree tolerance
                msg.twist.angular.z = 0.0
                self.start_x = self.current_x
                self.start_y = self.current_y
                self.state = State.RETURNING
                self.get_logger().info('U-Turn complete. Returning to start.')
            else:
                kp_angular = 1.0
                angular_cmd = self.clamp(kp_angular * error, 0.1, 0.5)
                msg.twist.angular.z = angular_cmd

        # -------------------------
        # 3. RETURN 1 METER
        # -------------------------
        elif self.state == State.RETURNING:
            target_distance = 1.0
            distance_traveled = math.sqrt(
                (self.current_x - self.start_x)**2 +
                (self.current_y - self.start_y)**2
            )

            error = target_distance - distance_traveled

            if error <= 0.02:  # 2cm tolerance
                msg.twist.linear.x = 0.0
                self.state = State.FINISHED
                self.get_logger().info('Successfully returned to start!')
            else:
                kp_linear = 0.5
                linear_cmd = self.clamp(kp_linear * error, 0.05, 0.2)
                msg.twist.linear.x = linear_cmd

        # -------------------------
        # 4. FINISHED
        # -------------------------
        elif self.state == State.FINISHED:
            msg.twist.linear.x = 0.0
            msg.twist.angular.z = 0.0

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = OutAndBackController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()