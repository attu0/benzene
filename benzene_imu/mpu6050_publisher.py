#!/usr/bin/env python3
"""
MPU6050 I2C IMU driver.

Publishes raw (unfiltered) IMU data on /imu/data_raw as sensor_msgs/Imu.
Orientation is left unset (covariance[0] = -1) since this node does not
compute orientation — feed this into imu_filter_madgwick to get a real
orientation quaternion on /imu/data before fusing into an EKF.

Runs a short stationary gyro-bias calibration on startup. Keep the robot
still until the "Calibration done" log line appears.
"""

import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from smbus2 import SMBus

# MPU6050 register map
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Default full-scale ranges: accel ±2g, gyro ±250 deg/s
ACCEL_SCALE = 16384.0   # LSB/g
GYRO_SCALE = 131.0      # LSB/(deg/s)
GRAVITY = 9.80665       # m/s^2 per g

DEG_TO_RAD = math.pi / 180.0


def read_word_2c(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val = -((65535 - val) + 1)
    return val


class Mpu6050Publisher(Node):

    def __init__(self):
        super().__init__('mpu6050_publisher')

        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('i2c_address', 0x68)
        self.declare_parameter('frame_id', 'imu_link')
        self.declare_parameter('publish_rate', 100.0)
        self.declare_parameter('calibration_samples', 400)

        self.i2c_bus_num = self.get_parameter('i2c_bus').value
        self.i2c_address = self.get_parameter('i2c_address').value
        self.frame_id = self.get_parameter('frame_id').value
        publish_rate = self.get_parameter('publish_rate').value
        self.calibration_samples = self.get_parameter('calibration_samples').value

        self.publisher_ = self.create_publisher(Imu, '/imu/data_raw', 10)

        try:
            self.bus = SMBus(self.i2c_bus_num)
        except FileNotFoundError:
            self.get_logger().fatal(
                f'Could not open /dev/i2c-{self.i2c_bus_num}. '
                'Is I2C enabled (raspi-config) and are you in the i2c group?'
            )
            raise

        self._wake_up_sensor()

        self.gyro_bias = (0.0, 0.0, 0.0)
        self._calibrate()

        period = 1.0 / publish_rate
        self.timer = self.create_timer(period, self._timer_callback)
        self.get_logger().info('mpu6050_publisher running.')

    def _wake_up_sensor(self):
        # MPU6050 starts in sleep mode — must clear PWR_MGMT_1 first
        self.bus.write_byte_data(self.i2c_address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # 1kHz sample rate / (1 + SMPLRT_DIV) — 0x07 -> 125Hz internal
        self.bus.write_byte_data(self.i2c_address, SMPLRT_DIV, 0x07)
        # Digital low-pass filter, ~44Hz bandwidth — reduces vibration noise
        self.bus.write_byte_data(self.i2c_address, CONFIG, 0x03)
        # Gyro ±250 deg/s (default, register value 0x00)
        self.bus.write_byte_data(self.i2c_address, GYRO_CONFIG, 0x00)
        # Accel ±2g (default, register value 0x00)
        self.bus.write_byte_data(self.i2c_address, ACCEL_CONFIG, 0x00)
        time.sleep(0.1)

    def _read_raw(self):
        ax = read_word_2c(self.bus, self.i2c_address, ACCEL_XOUT_H) / ACCEL_SCALE * GRAVITY
        ay = read_word_2c(self.bus, self.i2c_address, ACCEL_XOUT_H + 2) / ACCEL_SCALE * GRAVITY
        az = read_word_2c(self.bus, self.i2c_address, ACCEL_XOUT_H + 4) / ACCEL_SCALE * GRAVITY
        gx = read_word_2c(self.bus, self.i2c_address, GYRO_XOUT_H) / GYRO_SCALE * DEG_TO_RAD
        gy = read_word_2c(self.bus, self.i2c_address, GYRO_XOUT_H + 2) / GYRO_SCALE * DEG_TO_RAD
        gz = read_word_2c(self.bus, self.i2c_address, GYRO_XOUT_H + 4) / GYRO_SCALE * DEG_TO_RAD
        return (ax, ay, az), (gx, gy, gz)

    def _calibrate(self):
        self.get_logger().info(
            f'Calibrating gyro bias over {self.calibration_samples} samples — '
            'keep the robot completely still...'
        )
        sx = sy = sz = 0.0
        n = 0
        for _ in range(self.calibration_samples):
            try:
                _, (gx, gy, gz) = self._read_raw()
            except OSError as exc:
                self.get_logger().warn(f'I2C read failed during calibration: {exc}')
                continue
            sx += gx
            sy += gy
            sz += gz
            n += 1
            time.sleep(0.005)

        if n == 0:
            self.get_logger().error(
                'Calibration got zero successful reads — check wiring/I2C bus.'
            )
            return

        self.gyro_bias = (sx / n, sy / n, sz / n)
        self.get_logger().info(
            f'Calibration done. Gyro bias (rad/s): '
            f'x={self.gyro_bias[0]:.5f} y={self.gyro_bias[1]:.5f} z={self.gyro_bias[2]:.5f}'
        )

    def _timer_callback(self):
        try:
            (ax, ay, az), (gx, gy, gz) = self._read_raw()
        except OSError as exc:
            self.get_logger().warn(f'I2C read failed: {exc}', throttle_duration_sec=2.0)
            return

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        # No orientation computed here — imu_filter_madgwick fills this in
        msg.orientation_covariance[0] = -1.0

        msg.angular_velocity.x = gx - self.gyro_bias[0]
        msg.angular_velocity.y = gy - self.gyro_bias[1]
        msg.angular_velocity.z = gz - self.gyro_bias[2]
        msg.angular_velocity_covariance = [
            0.02, 0.0, 0.0,
            0.0, 0.02, 0.0,
            0.0, 0.0, 0.02,
        ]

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az
        msg.linear_acceleration_covariance = [
            0.04, 0.0, 0.0,
            0.0, 0.04, 0.0,
            0.0, 0.0, 0.04,
        ]

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = Mpu6050Publisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()