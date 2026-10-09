/**
 * @file square_diff_odom_controller.cpp
 * @brief Controls a differential drive robot using Odometry for perfect 90-degree turns
 */

#include <chrono>
#include <cmath>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"

using namespace std::chrono_literals;

class SquareController : public rclcpp::Node
{
public:
    SquareController() : Node("square_controller")
    {
        publisher_ = create_publisher<geometry_msgs::msg::TwistStamped>(
            "/diff_drive_controller/cmd_vel", 10);

        odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
            "/diff_drive_controller/odom", 10,
            std::bind(&SquareController::odom_callback, this, std::placeholders::_1));

        // Use a faster 50ms timer for more precise velocity updates
        timer_ = create_wall_timer(
            50ms, std::bind(&SquareController::control_loop, this));

        current_side_ = 0;
        state_ = MOVING;
        got_odom_ = false;
        initialized_ = false;

        RCLCPP_INFO(get_logger(), "Starting precise odometry-based square movement");
    }

private:
    enum State { MOVING, TURNING, FINISHED };

    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        current_x_ = msg->pose.pose.position.x;
        current_y_ = msg->pose.pose.position.y;

        // Convert Quaternion to Euler angles to extract current Yaw
        auto q = msg->pose.pose.orientation;
        tf2::Quaternion quaternion(q.x, q.y, q.z, q.w);
        double roll, pitch;

        tf2::Matrix3x3(quaternion).getRPY(roll, pitch, current_yaw_);
        got_odom_ = true;
    }

    // Handles math when the turn crosses the Pi / -Pi boundary
    double normalize_angle(double angle)
    {
        while (angle > M_PI) angle -= 2.0 * M_PI;
        while (angle < -M_PI) angle += 2.0 * M_PI;
        return angle;
    }

void control_loop()
    {
        if (!got_odom_)
        {
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "Waiting for /odom...");
            return;
        }

        geometry_msgs::msg::TwistStamped cmd;
        cmd.header.stamp = now();
        cmd.header.frame_id = "base_link";

        if (!initialized_)
        {
            start_x_ = current_x_;
            start_y_ = current_y_;
            initialized_ = true;
        }

        // -------------------------
        // MOVE FORWARD (P-Controller)
        // -------------------------
        if (state_ == MOVING)
        {
            double target_distance = 1.0;
            double distance_traveled = std::sqrt(
                std::pow(current_x_ - start_x_, 2) +
                std::pow(current_y_ - start_y_, 2));

            double error = target_distance - distance_traveled;
            double tolerance = 0.02; // 2 cm tolerance

            if (error <= tolerance)
            {
                cmd.twist.linear.x = 0.0;
                turn_start_yaw_ = current_yaw_;
                state_ = TURNING;
                RCLCPP_INFO(get_logger(), "Side %d completed, starting smooth turn.", current_side_ + 1);
            }
            else
            {
                // Proportional control for linear speed
                double kp_linear = 0.5;
                double linear_cmd = kp_linear * error;

                // Clamp speeds to prevent moving too fast or too slow (motor deadband)
                linear_cmd = std::clamp(linear_cmd, 0.05, 0.2);
                cmd.twist.linear.x = linear_cmd;
            }
        }

        // -------------------------
        // TURN 90 DEGREES (P-Controller)
        // -------------------------
        else if (state_ == TURNING)
        {
            double target_angle = M_PI / 2.0;
            double angle_turned = normalize_angle(current_yaw_ - turn_start_yaw_);

            double error = target_angle - angle_turned;
            double tolerance = 0.02; // Approx 1.1 degrees tolerance

            // Stop turning when within the acceptable tolerance
            if (error <= tolerance)
            {
                cmd.twist.angular.z = 0.0;
                current_side_++;

                if (current_side_ >= 4)
                {
                    state_ = FINISHED;
                    RCLCPP_INFO(get_logger(), "Square completed!");
                }
                else
                {
                    start_x_ = current_x_;
                    start_y_ = current_y_;
                    state_ = MOVING;
                }
            }
            else
            {
                // Proportional control for angular speed
                double kp_angular = 1.2;
                double angular_cmd = kp_angular * error;

                // Clamp speeds: Max 0.4 rad/s, Min 0.1 rad/s (to overcome wheel friction)
                angular_cmd = std::clamp(angular_cmd, 0.1, 0.4);
                cmd.twist.angular.z = angular_cmd;
            }
        }

        // -------------------------
        // FINISHED
        // -------------------------
        else if (state_ == FINISHED)
        {
            cmd.twist.linear.x = 0.0;
            cmd.twist.angular.z = 0.0;
        }

        publisher_->publish(cmd);
    }

    rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    double current_x_ = 0.0, current_y_ = 0.0, current_yaw_ = 0.0;
    double start_x_, start_y_, turn_start_yaw_;

    bool got_odom_, initialized_;
    int current_side_;
    State state_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SquareController>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}