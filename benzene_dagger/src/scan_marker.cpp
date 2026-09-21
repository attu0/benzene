#include <cmath>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "geometry_msgs/msg/point.hpp"

class LidarVisualizerNode : public rclcpp::Node
{
public:
  LidarVisualizerNode()
  : Node("lidar_visualizer_node")
  {
    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan",
      10,
      std::bind(
        &LidarVisualizerNode::scanCallback,
        this,
        std::placeholders::_1));

    publisher_ = this->create_publisher<visualization_msgs::msg::Marker>(
      "/scan_rays",
      10);

    RCLCPP_INFO(
      this->get_logger(),
      "LiDAR Visualizer Node started. Publishing to /scan_rays");
  }

private:
  void scanCallback(
    const sensor_msgs::msg::LaserScan::SharedPtr msg)
  {
    visualization_msgs::msg::Marker marker;

    marker.header.frame_id = msg->header.frame_id;
    marker.header.stamp = msg->header.stamp;

    marker.ns = "lidar_rays";
    marker.id = 0;

    marker.type = visualization_msgs::msg::Marker::LINE_LIST;
    marker.action = visualization_msgs::msg::Marker::ADD;

    // Light blue and semi-transparent.
    marker.color.r = 0.4;
    marker.color.g = 0.8;
    marker.color.b = 1.0;
    marker.color.a = 0.3;

    // Line thickness.
    marker.scale.x = 0.005;

    // No pose offset.
    marker.pose.orientation.w = 1.0;

    float angle = msg->angle_min;

    for (const float range : msg->ranges) {
      if (std::isfinite(range) &&
          range >= msg->range_min &&
          range <= msg->range_max)
      {
        // Start point: LiDAR origin.
        geometry_msgs::msg::Point start_point;
        start_point.x = 0.0;
        start_point.y = 0.0;
        start_point.z = 0.0;

        // End point: LiDAR measurement.
        geometry_msgs::msg::Point end_point;
        end_point.x = range * std::cos(angle);
        end_point.y = range * std::sin(angle);
        end_point.z = 0.0;

        marker.points.push_back(start_point);
        marker.points.push_back(end_point);
      }

      angle += msg->angle_increment;
    }

    publisher_->publish(marker);
  }

  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr
    subscription_;

  rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr
    publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<LidarVisualizerNode>();

  try {
    rclcpp::spin(node);
  } catch (const rclcpp::exceptions::RCLError & e) {
    RCLCPP_ERROR(
      node->get_logger(),
      "ROS 2 error: %s",
      e.what());
  }

  rclcpp::shutdown();

  return 0;
}