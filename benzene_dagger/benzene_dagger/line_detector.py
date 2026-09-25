#!/usr/bin/env python3

"""Multi-point yellow centerline detector for the Benzene robot."""

import cv2
import numpy as np

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Float32


class YellowLineDetector(Node):
    """Detect the yellow centerline and calculate steering errors."""

    def __init__(self):
        super().__init__('yellow_line_detector')

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/cam_1/color/image_raw',
            self.image_callback,
            10,
        )

        self.lateral_error_pub = self.create_publisher(
            Float32,
            '/line/lateral_error',
            10,
        )

        self.heading_error_pub = self.create_publisher(
            Float32,
            '/line/heading_error',
            10,
        )

        self.get_logger().info(
            'Multi-point yellow line detector started.'
        )

    def image_callback(self, msg):
        """Process the camera image."""

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8',
            )
        except Exception as exc:
            self.get_logger().error(
                f'Failed to convert image: {exc}'
            )
            return

        height, width = frame.shape[:2]

        # ---------------------------------------------------------
        # Region of interest
        # ---------------------------------------------------------

        roi_start = int(height * 0.35)

        roi = frame[roi_start:height, :]

        roi_height = roi.shape[0]

        # ---------------------------------------------------------
        # Convert BGR to HSV
        # ---------------------------------------------------------

        hsv = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2HSV,
        )

        # Yellow threshold.
        lower_yellow = np.array(
            [20, 100, 100],
            dtype=np.uint8,
        )

        upper_yellow = np.array(
            [40, 255, 255],
            dtype=np.uint8,
        )

        mask = cv2.inRange(
            hsv,
            lower_yellow,
            upper_yellow,
        )

        # ---------------------------------------------------------
        # Clean the mask
        # ---------------------------------------------------------

        kernel = np.ones(
            (5, 5),
            np.uint8,
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel,
        )

        # ---------------------------------------------------------
        # Find yellow contours
        # ---------------------------------------------------------

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        valid_contours = [
            contour
            for contour in contours
            if cv2.contourArea(contour) > 100
        ]

        # ---------------------------------------------------------
        # Detect line position at multiple heights
        # ---------------------------------------------------------

        sample_rows = [
            int(roi_height * 0.30),
            int(roi_height * 0.60),
            int(roi_height * 0.90),
        ]

        detected_points = []

        for row in sample_rows:

            # Search within a small vertical band.
            band_height = 12

            y_start = max(
                0,
                row - band_height,
            )

            y_end = min(
                roi_height,
                row + band_height,
            )

            yellow_pixels = np.where(
                mask[y_start:y_end, :] > 0
            )

            if yellow_pixels[1].size == 0:
                continue

            x_values = yellow_pixels[1]

            # Median is more robust than simply taking the mean.
            x = int(np.median(x_values))

            detected_points.append(
                (x, row)
            )

        # ---------------------------------------------------------
        # Draw sample points
        # ---------------------------------------------------------

        for index, (x, y) in enumerate(
            detected_points
        ):

            cv2.circle(
                roi,
                (x, y),
                8,
                (0, 0, 255),
                -1,
            )

            cv2.putText(
                roi,
                f'P{index + 1}',
                (x + 10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

        # ---------------------------------------------------------
        # Image center
        # ---------------------------------------------------------

        image_center = width // 2

        cv2.line(
            roi,
            (image_center, 0),
            (image_center, roi_height),
            (255, 0, 0),
            2,
        )

        # ---------------------------------------------------------
        # Calculate errors
        # ---------------------------------------------------------

        lateral_error = None
        heading_error = None

        if len(detected_points) >= 2:

            # Closest point to the robot.
            near_x, near_y = detected_points[-1]

            # Furthest visible point.
            far_x, far_y = detected_points[0]

            # -----------------------------------------------------
            # Lateral error
            # -----------------------------------------------------

            lateral_error = float(
                near_x - image_center
            )

            # -----------------------------------------------------
            # Heading error
            #
            # Positive:
            # line moves toward the right as it gets farther away.
            #
            # Negative:
            # line moves toward the left.
            # -----------------------------------------------------

            dx = float(far_x - near_x)
            dy = float(far_y - near_y)

            heading_error = np.arctan2(
                dx,
                abs(dy),
            )

            heading_error = float(
                heading_error
            )

            # -----------------------------------------------------
            # Draw line connecting detected points
            # -----------------------------------------------------

            for i in range(
                len(detected_points) - 1
            ):

                cv2.line(
                    roi,
                    detected_points[i],
                    detected_points[i + 1],
                    (0, 255, 0),
                    3,
                )

            # -----------------------------------------------------
            # Draw lateral error
            # -----------------------------------------------------

            cv2.line(
                roi,
                (
                    image_center,
                    near_y,
                ),
                (
                    near_x,
                    near_y,
                ),
                (255, 255, 0),
                3,
            )

            # -----------------------------------------------------
            # Display values
            # -----------------------------------------------------

            cv2.putText(
                roi,
                f'Lateral: {lateral_error:.1f}',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                roi,
                f'Heading: {heading_error:.3f}',
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            # -----------------------------------------------------
            # Publish lateral error
            # -----------------------------------------------------

            lateral_msg = Float32()
            lateral_msg.data = lateral_error

            self.lateral_error_pub.publish(
                lateral_msg
            )

            # -----------------------------------------------------
            # Publish heading error
            # -----------------------------------------------------

            heading_msg = Float32()
            heading_msg.data = heading_error

            self.heading_error_pub.publish(
                heading_msg
            )

        else:

            cv2.putText(
                roi,
                'LINE NOT DETECTED',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        # ---------------------------------------------------------
        # Display
        # ---------------------------------------------------------

        cv2.imshow(
            'Benzene - Multi Point Line Detection',
            frame,
        )

        cv2.imshow(
            'Yellow Mask',
            mask,
        )

        cv2.waitKey(1)


def main(args=None):
    """Run the yellow line detector."""

    rclpy.init(args=args)

    node = YellowLineDetector()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()