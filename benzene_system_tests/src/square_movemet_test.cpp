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
        publisher_ =
            create_publisher<geometry_msgs::msg::TwistStamped>(
                "/diff_drive_controller/cmd_vel", 10);

        odom_sub_ =
            create_subscription<nav_msgs::msg::Odometry>(
                "/diff_drive_controller/odom",
                10,
                std::bind(
                    &SquareController::odom_callback,
                    this,
                    std::placeholders::_1));

        timer_ =
            create_wall_timer(
                50ms,
                std::bind(
                    &SquareController::control_loop,
                    this));

        current_side_ = 0;
        state_ = MOVING;

        start_x_ = 0.0;
        start_y_ = 0.0;

        turn_start_yaw_ = 0.0;

        got_odom_ = false;
        initialized_ = false;

        RCLCPP_INFO(
            get_logger(),
            "Square controller started");
    }

private:

    enum State
    {
        MOVING,
        TURNING,
        FINISHED
    };

    void odom_callback(
        const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        current_x_ =
            msg->pose.pose.position.x;

        current_y_ =
            msg->pose.pose.position.y;

        auto q =
            msg->pose.pose.orientation;

        tf2::Quaternion quaternion(
            q.x,
            q.y,
            q.z,
            q.w);

        double roll, pitch;

        tf2::Matrix3x3(quaternion).getRPY(
            roll,
            pitch,
            current_yaw_);

        got_odom_ = true;
    }

    double normalize_angle(double angle)
    {
        while (angle > M_PI)
            angle -= 2.0 * M_PI;

        while (angle < -M_PI)
            angle += 2.0 * M_PI;

        return angle;
    }

    void control_loop()
    {
        if (!got_odom_)
        {
            RCLCPP_WARN_THROTTLE(
                get_logger(),
                *get_clock(),
                2000,
                "Waiting for /odom...");
            return;
        }

        geometry_msgs::msg::TwistStamped cmd;

        cmd.header.stamp = now();
        cmd.header.frame_id = "base_link";

        // Initialize starting position
        if (!initialized_)
        {
            start_x_ = current_x_;
            start_y_ = current_y_;

            initialized_ = true;

            RCLCPP_INFO(
                get_logger(),
                "Starting square movement");
        }

        // -------------------------
        // MOVE FORWARD
        // -------------------------

        if (state_ == MOVING)
        {
            cmd.twist.linear.x = 0.2;

            double distance =
                std::sqrt(
                    std::pow(current_x_ - start_x_, 2) +
                    std::pow(current_y_ - start_y_, 2));

            // Move 1 meter
            if (distance >= 1.0)
            {
                cmd.twist.linear.x = 0.0;

                turn_start_yaw_ =
                    current_yaw_;

                state_ = TURNING;

                RCLCPP_INFO(
                    get_logger(),
                    "Side %d completed",
                    current_side_ + 1);
            }
        }

        // -------------------------
        // TURN 90 DEGREES
        // -------------------------

        else if (state_ == TURNING)
        {
            cmd.twist.angular.z = 0.4;

            double angle_turned =
                normalize_angle(
                    current_yaw_ -
                    turn_start_yaw_);

            // Turn left 90 degrees
            if (angle_turned >= M_PI / 2.0)
            {
                cmd.twist.angular.z = 0.0;

                current_side_++;

                if (current_side_ >= 4)
                {
                    state_ = FINISHED;

                    RCLCPP_INFO(
                        get_logger(),
                        "Square completed!");
                }
                else
                {
                    start_x_ =
                        current_x_;

                    start_y_ =
                        current_y_;

                    state_ = MOVING;

                    RCLCPP_INFO(
                        get_logger(),
                        "Starting side %d",
                        current_side_ + 1);
                }
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

    // ROS

    rclcpp::Publisher<
        geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;

    rclcpp::Subscription<
        nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

    rclcpp::TimerBase::SharedPtr timer_;

    // Robot position

    double current_x_ = 0.0;
    double current_y_ = 0.0;
    double current_yaw_ = 0.0;

    double start_x_;
    double start_y_;

    double turn_start_yaw_;

    bool got_odom_;
    bool initialized_;

    int current_side_;

    State state_;
};


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node =
        std::make_shared<SquareController>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}