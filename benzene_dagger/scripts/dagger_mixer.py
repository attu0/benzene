#!/usr/bin/env python3

"""DAgger mixer: the only node that publishes to the robot's drive topic.

    /expert/cmd_vel   (TwistStamped) --\
                                        >-- mixer --> /diff_drive_controller/cmd_vel (TwistStamped)
    /learner/cmd_vel  (TwistStamped) --/

With probability `beta` the expert drives, otherwise the learner drives.
The choice is re-sampled every `mix_hold_time` seconds (not every tick),
so the robot does not jitter between two policies.

    beta = 1.0  -> pure expert (behavioral-cloning data collection)
    beta = 0.0  -> pure learner (policy evaluation / pure DAgger rollout)
    0 < beta < 1 -> DAgger mixture

beta can be changed live:
    ros2 param set /dagger_mixer beta 0.5
"""

import random

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from std_msgs.msg import String


class DaggerMixer(Node):

    def __init__(self):
        super().__init__('dagger_mixer')

        self.declare_parameter('beta', 1.0)
        self.declare_parameter('mix_hold_time', 1.0)
        self.declare_parameter('rate', 20.0)
        self.declare_parameter('source_timeout', 0.5)
        self.declare_parameter('expert_topic', '/expert/cmd_vel')
        self.declare_parameter('learner_topic', '/learner/cmd_vel')
        self.declare_parameter('drive_topic', '/diff_drive_controller/cmd_vel')

        expert_topic = self.get_parameter('expert_topic').value
        learner_topic = self.get_parameter('learner_topic').value
        drive_topic = self.get_parameter('drive_topic').value
        rate = float(self.get_parameter('rate').value)

        self.latest = {'expert': None, 'learner': None}
        self.latest_time = {'expert': None, 'learner': None}

        self.source = 'expert'
        self.hold_until = self.get_clock().now()

        self.create_subscription(
            TwistStamped, expert_topic,
            lambda m: self._store('expert', m), 10)
        self.create_subscription(
            TwistStamped, learner_topic,
            lambda m: self._store('learner', m), 10)

        self.drive_pub = self.create_publisher(
            TwistStamped, drive_topic, 10)
        self.source_pub = self.create_publisher(
            String, '/dagger/active_source', 10)

        self.create_timer(1.0 / rate, self.tick)

        self.get_logger().info(
            f'Mixer started: expert={expert_topic}, '
            f'learner={learner_topic}, drive={drive_topic}, '
            f'beta={self.get_parameter("beta").value:.2f}')

    def _store(self, name, msg):
        self.latest[name] = msg
        self.latest_time[name] = self.get_clock().now()

    def _is_fresh(self, name):
        stamp = self.latest_time[name]
        if stamp is None:
            return False
        timeout = float(self.get_parameter('source_timeout').value)
        age = (self.get_clock().now() - stamp).nanoseconds / 1e9
        return age <= timeout

    def _update_source(self):
        now = self.get_clock().now()
        if now < self.hold_until:
            return

        beta = min(1.0, max(0.0, float(self.get_parameter('beta').value)))
        self.source = 'expert' if random.random() < beta else 'learner'

        hold = float(self.get_parameter('mix_hold_time').value)
        self.hold_until = now + rclpy.duration.Duration(seconds=hold)

    def tick(self):
        self._update_source()

        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = 'base_link'

        if self._is_fresh(self.source):
            out.twist = self.latest[self.source].twist
        else:
            # Chosen source is silent (e.g. line lost / camera dead): stop.
            self.get_logger().warn(
                f'"{self.source}" command is stale. Stopping robot.',
                throttle_duration_sec=2.0)

        self.drive_pub.publish(out)
        self.source_pub.publish(String(data=self.source))

    def stop_robot(self):
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = 'base_link'
        self.drive_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = DaggerMixer()
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