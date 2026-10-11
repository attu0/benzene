/**
 * @file detected_dock_pose_publisher.cpp
 * @brief Publishes the pose of an AprilTag located on/near a docking station
 *
 * This program detects an AprilTag that is mounted near or on a docking station and publishes
 * its pose relative to the camera optical frame. The optical frame follows the typical computer
 * vision convention where:
 *   - Z forward (pointing out from the camera)
 *   - X right
 *   - Y down
 *
 * The node subscribes to TF2 transforms published by the AprilTag detection system between the
 * camera's optical frame and the detected tag's frame. It then republishes these transforms as
 * PoseStamped messages that can be used by the Nav2 docking system to compute the actual
 * docking pose.
 *
 * Subscription Topics:
 *     /tf (tf2_msgs/TFMessage): Transform tree containing camera optical frame to tag transforms
 *
 * Publishing Topics:
 *     /detected_dock_pose (geometry_msgs/PoseStamped): Pose of the detected AprilTag relative
 *                                                      to the camera optical frame
 *
 * Parameters:
 *     parent_frame (string, default: "cam_1_optical"): Name of the camera's optical frame
 *     child_frame (string, default: "tag36h11:0"): Name of the AprilTag frame
 *     publish_rate (double, default: 10.0): How often to publish the tag pose in Hz
 *     max_tf_age (double, default: 0.5): Max age in seconds of the tag transform before it is
 *                                        considered stale and not published
 *
 * @author Addison Sears-Collins
 * @date December 11, 2024
 */

#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"

/**
 * @brief A ROS2 node that publishes AprilTag poses relative to the camera optical frame
 *
 * This node listens for transforms between the camera's optical frame (cam_1_optical)
 * and an AprilTag frame (tag36h11:0). The optical frame is important as it follows standard
 * computer vision conventions and is the frame in which the AprilTag detector operates.
 *
 * The AprilTag is mounted near or on a docking station, and this node publishes the tag's pose
 * in the optical frame coordinate system. The Nav2 docking system can then use this tag pose
 * as a reference to compute the actual docking position.
 */
class DetectedDockPosePublisher : public rclcpp::Node
{
public:
  /**
   * @brief Constructor for the DetectedDockPosePublisher node
   *
   * Initializes the node, sets up parameters, and creates publishers and transform listeners
   */
  DetectedDockPosePublisher()
  : Node("detected_dock_pose_publisher")
  {
    // Declare parameters with default values and documentation
    this->declare_parameter("parent_frame", "cam_1_optical");
    this->declare_parameter("child_frame", "tag36h11:0");
    this->declare_parameter("publish_rate", 10.0);  // Hz
    this->declare_parameter("max_tf_age", 0.5);     // seconds

    // Get the values of our parameters
    parent_frame_ = this->get_parameter("parent_frame").as_string();
    child_frame_ = this->get_parameter("child_frame").as_string();
    double publish_rate = this->get_parameter("publish_rate").as_double();
    max_tf_age_ = this->get_parameter("max_tf_age").as_double();

    // Guard against a zero or negative rate (would divide by zero / give a negative period)
    if (publish_rate <= 0.0) {
      RCLCPP_WARN(this->get_logger(), "publish_rate must be > 0, falling back to 10.0 Hz");
      publish_rate = 10.0;
    }

    // Create a transform buffer to store and look up transforms
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());

    // Create a transform listener to receive transforms
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    // Create a publisher for the dock pose
    dock_pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
      "detected_dock_pose", 10);

    // Create a timer that will trigger pose updates
    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(static_cast<int>(1000.0 / publish_rate)),
      std::bind(&DetectedDockPosePublisher::timer_callback, this));

    // Log that we've successfully initialized
    RCLCPP_INFO(this->get_logger(),
      "Detected dock pose publisher initialized with parent frame: '%s' and child frame: '%s'",
      parent_frame_.c_str(), child_frame_.c_str());
  }

private:
  /**
   * @brief Timer callback that publishes the latest dock pose
   *
   * This function is called periodically to:
   * 1. Look up the latest transform between the camera and AprilTag
   * 2. Convert the transform into a pose message
   * 3. Publish the pose for the docking system to use
   */
  void timer_callback()
  {
    try {
      // Look up the latest transform
      geometry_msgs::msg::TransformStamped transform = tf_buffer_->lookupTransform(
        parent_frame_,
        child_frame_,
        tf2::TimePointZero // get latest transform
      );

      // Skip stale detections. The AprilTag node only updates this transform while the tag is
      // visible, so an old stamp means the tag was lost. Not publishing lets the docking server
      // detect the loss instead of being fed a frozen pose with a fresh timestamp.
      const rclcpp::Time now = this->get_clock()->now();
      const double age = (now - rclcpp::Time(transform.header.stamp)).seconds();
      if (age > max_tf_age_) {
        RCLCPP_WARN_THROTTLE(
          this->get_logger(), *this->get_clock(), 2000,
          "Tag transform '%s' -> '%s' is stale (%.2f s old), not publishing",
          parent_frame_.c_str(), child_frame_.c_str(), age);
        return;
      }

      geometry_msgs::msg::PoseStamped dock_pose;
      // Use the time the tag was actually detected, not "now"
      dock_pose.header.stamp = transform.header.stamp;
      dock_pose.header.frame_id = parent_frame_;

      dock_pose.pose.position.x = transform.transform.translation.x;
      dock_pose.pose.position.y = transform.transform.translation.y;
      dock_pose.pose.position.z = transform.transform.translation.z;
      dock_pose.pose.orientation = transform.transform.rotation;

      dock_pose_pub_->publish(dock_pose);
    }
    catch (const tf2::TransformException & ex) {
      // Throttled warning so a wrong frame name is visible without spamming the terminal
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 2000,
        "Could not get transform '%s' -> '%s': %s",
        parent_frame_.c_str(), child_frame_.c_str(), ex.what());
    }
  }

  // Frame names from parameters
  std::string parent_frame_; ///< Name of the camera frame
  std::string child_frame_;  ///< Name of the AprilTag frame
  double max_tf_age_{0.5};   ///< Max accepted age of the tag transform in seconds

  // ROS infrastructure
  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;        ///< Buffer for storing transforms
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_; ///< Listener for transforms
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr dock_pose_pub_; ///< Publisher for dock poses
  rclcpp::TimerBase::SharedPtr timer_;               ///< Timer for periodic publishing
};

/**
 * @brief Main function that starts the dock pose publisher node
 *
 * @param argc Number of command line arguments
 * @param argv Array of command line arguments
 * @return int Exit code (0 if successful)
 */
int main(int argc, char * argv[])
{
  // Initialize ROS
  rclcpp::init(argc, argv);
  // Create and spin (run) the node
  rclcpp::spin(std::make_shared<DetectedDockPosePublisher>());
  // Clean up ROS and exit
  rclcpp::shutdown();
  return 0;
}