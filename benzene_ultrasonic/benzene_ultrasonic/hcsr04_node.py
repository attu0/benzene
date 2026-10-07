import statistics
from collections import deque

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Range
from gpiozero import DistanceSensor


class UltrasonicHCSR04(Node):
    def __init__(self):
        super().__init__('ultrasonic_hcsr04')
        self.declare_parameter('trigger_pin', 23)
        self.declare_parameter('echo_pin', 24)
        self.declare_parameter('frame_id', 'ultrasonic')
        self.declare_parameter('rate_hz', 10.0)
        self.declare_parameter('min_range', 0.02)
        self.declare_parameter('max_range', 4.0)
        self.declare_parameter('field_of_view', 0.26)
        self.declare_parameter('median_window', 5)

        self.min_range = self.get_parameter('min_range').value
        self.max_range = self.get_parameter('max_range').value
        self.window = deque(maxlen=self.get_parameter('median_window').value)

        self.sensor = DistanceSensor(
            echo=self.get_parameter('echo_pin').value,
            trigger=self.get_parameter('trigger_pin').value,
            max_distance=self.max_range,
            queue_len=1)

        self.pub = self.create_publisher(
            Range, 'ultrasonic/range', qos_profile_sensor_data)
        self.create_timer(1.0 / self.get_parameter('rate_hz').value, self.tick)

    def tick(self):
        d = float(self.sensor.distance)  # metres; max_distance when no echo
        if d < self.min_range:
            d = self.max_range
        self.window.append(d)

        # median rejects the single-sample spikes seen with software timing
        filtered = statistics.median(self.window)

        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = self.get_parameter('field_of_view').value
        msg.min_range = self.min_range
        msg.max_range = self.max_range
        msg.range = (float('inf')
                     if filtered >= self.max_range - 1e-3 else filtered)
        self.pub.publish(msg)

    def destroy_node(self):
        self.sensor.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = UltrasonicHCSR04()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()