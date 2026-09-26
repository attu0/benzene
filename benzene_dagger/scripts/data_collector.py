#!/usr/bin/env python3

"""Records synchronized (camera image, expert action) pairs for DAgger/behavior cloning."""

import csv
import os
import time

import cv2
import message_filters
import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped


class DataCollector(Node):
    """Subscribe to image + expert action, save synced pairs to disk."""

    def __init__(self):
        super().__init__('data_collector')

        self.declare_parameter('dataset_dir', os.path.expanduser('~/ros2_ws/src/benzene/benzene_dagger/dataset'))
        self.declare_parameter('episode_name', '')
        self.declare_parameter('sync_slop', 0.05)  # seconds

        dataset_root = self.get_parameter('dataset_dir').value
        episode_name = self.get_parameter('episode_name').value

        if not episode_name:
            episode_name = time.strftime('episode_%Y%m%d_%H%M%S')

        self.episode_dir = os.path.join(dataset_root, episode_name)
        self.images_dir = os.path.join(self.episode_dir, 'images')
        os.makedirs(self.images_dir, exist_ok=True)

        self.csv_path = os.path.join(self.episode_dir, 'labels.csv')
        self.csv_file = open(self.csv_path, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(
            ['frame', 'image_file', 'stamp_sec', 'linear_x', 'angular_z']
        )

        self.bridge = CvBridge()
        self.frame_count = 0

        image_sub = message_filters.Subscriber(
            self, Image, '/cam_1/color/image_raw'
        )
        action_sub = message_filters.Subscriber(
            self, TwistStamped, '/expert/cmd_vel'
        )

        slop = self.get_parameter('sync_slop').value

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [image_sub, action_sub],
            queue_size=10,
            slop=slop,
        )
        self.sync.registerCallback(self.synced_callback)

        self.get_logger().info(
            f'Recording to {self.episode_dir}'
        )

    def synced_callback(self, image_msg, twist_stamped_msg):
        """Save one synced (image, action) pair."""

        try:
            frame = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
        except Exception as exc:
            self.get_logger().error(f'Failed to convert image: {exc}')
            return

        twist_msg = twist_stamped_msg.twist

        image_filename = f'{self.frame_count:06d}.jpg'
        image_path = os.path.join(self.images_dir, image_filename)

        cv2.imwrite(image_path, frame)

        stamp_sec = image_msg.header.stamp.sec + image_msg.header.stamp.nanosec * 1e-9

        self.csv_writer.writerow([
            self.frame_count,
            image_filename,
            f'{stamp_sec:.6f}',
            f'{twist_msg.linear.x:.6f}',
            f'{twist_msg.angular.z:.6f}',
        ])

        if self.frame_count % 50 == 0:
            self.csv_file.flush()
            self.get_logger().info(f'Recorded {self.frame_count} frames')

        self.frame_count += 1

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = DataCollector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info(
            f'Saved {node.frame_count} frames to {node.episode_dir}'
        )
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()