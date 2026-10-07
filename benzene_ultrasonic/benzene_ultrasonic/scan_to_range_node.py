#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, Range


class UltrasonicScanToRange(Node):
    def __init__(self):
        super().__init__('ultrasonic_scan_to_range')
        self.declare_parameter('input_topic', 'ultrasonic/scan')
        self.declare_parameter('output_topic', 'ultrasonic/range')

        self.pub = self.create_publisher(
            Range, self.get_parameter('output_topic').value, qos_profile_sensor_data)
        self.create_subscription(
            LaserScan, self.get_parameter('input_topic').value,
            self.cb, qos_profile_sensor_data)

    def cb(self, scan: LaserScan):
        valid = [r for r in scan.ranges
                 if math.isfinite(r) and scan.range_min <= r <= scan.range_max]
        msg = Range()
        msg.header = scan.header
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = scan.angle_max - scan.angle_min
        msg.min_range = scan.range_min
        msg.max_range = scan.range_max
        msg.range = min(valid) if valid else float('inf')
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = UltrasonicScanToRange()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()