#!/usr/bin/env python3

"""
Benzene CNN behavioral-cloning controller.

Camera image -> CNN -> angular velocity -> robot

The model was trained to predict angular_z from the
camera image. Linear velocity remains fixed.
"""

import os

import cv2
import numpy as np
import torch
import torch.nn as nn

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped

from cv_bridge import CvBridge


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/models/benzene_bc_model.pth"
)

IMAGE_SIZE = (200, 120)

LINEAR_SPEED = 0.20

MAX_ANGULAR_VELOCITY = 0.8

CAMERA_TIMEOUT = 0.5


# ============================================================
# CNN
# ============================================================

class BenzeneCNN(nn.Module):

    def __init__(self):

        super().__init__()

        self.features = nn.Sequential(

            nn.Conv2d(3, 24, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(24, 36, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(36, 48, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(48, 64, kernel_size=3),
            nn.ReLU(),

            nn.Conv2d(64, 64, kernel_size=3),
            nn.ReLU(),

            nn.Flatten()
        )

        with torch.no_grad():

            dummy = torch.zeros(
                1,
                3,
                IMAGE_SIZE[1],
                IMAGE_SIZE[0]
            )

            feature_size = self.features(dummy).shape[1]

        self.regressor = nn.Sequential(

            nn.Linear(feature_size, 100),
            nn.ReLU(),

            nn.Linear(100, 50),
            nn.ReLU(),

            nn.Linear(50, 10),
            nn.ReLU(),

            nn.Linear(10, 1)
        )

    def forward(self, x):

        x = self.features(x)

        return self.regressor(x).squeeze(1)


# ============================================================
# CNN Controller
# ============================================================

class CNNController(Node):

    def __init__(self):

        super().__init__("cnn_controller")

        self.bridge = CvBridge()

        # ----------------------------------------------------
        # Device
        # ----------------------------------------------------

        self.device = torch.device(
            "cuda" if torch.cuda.is_available()
            else "cpu"
        )

        self.get_logger().info(
            f"Using device: {self.device}"
        )

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        self.model = BenzeneCNN()

        checkpoint = torch.load(
            MODEL_PATH,
            map_location=self.device
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.to(self.device)

        self.model.eval()

        self.get_logger().info(
            f"Loaded model: {MODEL_PATH}"
        )

        if "best_val_loss" in checkpoint:

            self.get_logger().info(
                f"Model validation loss: "
                f"{checkpoint['best_val_loss']:.6f}"
            )

        # ----------------------------------------------------
        # ROS interfaces
        # ----------------------------------------------------

        self.image_sub = self.create_subscription(
            Image,
            "/cam_1/color/image_raw",
            self.image_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            "/diff_drive_controller/cmd_vel",
            10
        )

        # ----------------------------------------------------
        # Safety
        # ----------------------------------------------------

        self.last_image_time = self.get_clock().now()

        self.safety_timer = self.create_timer(
            0.1,
            self.safety_callback
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        self.frame_count = 0

        self.get_logger().info(
            "CNN controller ready."
        )

    # ========================================================
    # Image callback
    # ========================================================

    def image_callback(self, msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding="bgr8"
            )

        except Exception as e:

            self.get_logger().error(
                f"CV bridge error: {e}"
            )

            return

        self.last_image_time = self.get_clock().now()

        # ----------------------------------------------------
        # Preprocessing
        # ----------------------------------------------------

        image = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = cv2.resize(
            image,
            IMAGE_SIZE
        )

        image = image.astype(
            np.float32
        ) / 255.0

        image = np.transpose(
            image,
            (2, 0, 1)
        )

        image = torch.tensor(
            image,
            dtype=torch.float32,
            device=self.device
        )

        image = image.unsqueeze(0)

        # ----------------------------------------------------
        # CNN inference
        # ----------------------------------------------------

        with torch.no_grad():

            prediction = self.model(
                image
            )

        angular_z = prediction.item()

        # ----------------------------------------------------
        # Safety clamp
        # ----------------------------------------------------

        angular_z = float(
            np.clip(
                angular_z,
                -MAX_ANGULAR_VELOCITY,
                MAX_ANGULAR_VELOCITY
            )
        )

        # ----------------------------------------------------
        # Publish command
        # ----------------------------------------------------

        cmd = TwistStamped()

        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = "base_link"

        cmd.twist.linear.x = LINEAR_SPEED
        cmd.twist.linear.y = 0.0
        cmd.twist.linear.z = 0.0

        cmd.twist.angular.x = 0.0
        cmd.twist.angular.y = 0.0
        cmd.twist.angular.z = angular_z

        self.cmd_pub.publish(cmd)

        # ----------------------------------------------------
        # Debug output
        # ----------------------------------------------------

        self.frame_count += 1

        if self.frame_count % 30 == 0:

            self.get_logger().info(
                f"CNN command: "
                f"linear={LINEAR_SPEED:.3f}, "
                f"angular={angular_z:.4f}"
            )

    # ========================================================
    # Safety timeout
    # ========================================================

    def safety_callback(self):

        elapsed = (
            self.get_clock().now()
            - self.last_image_time
        ).nanoseconds / 1e9

        if elapsed > CAMERA_TIMEOUT:

            self.stop_robot()

    # ========================================================
    # Stop robot
    # ========================================================

def stop_robot(self):

    cmd = TwistStamped()

    cmd.header.stamp = self.get_clock().now().to_msg()
    cmd.header.frame_id = "base_link"

    cmd.twist.linear.x = 0.0
    cmd.twist.linear.y = 0.0
    cmd.twist.linear.z = 0.0

    cmd.twist.angular.x = 0.0
    cmd.twist.angular.y = 0.0
    cmd.twist.angular.z = 0.0

    self.cmd_pub.publish(cmd)


# ============================================================
# Main
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = CNNController()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    except Exception as e:

        print(f"CNN controller error: {e}")

    finally:

        if node is not None:

            node.stop_robot()
            node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()