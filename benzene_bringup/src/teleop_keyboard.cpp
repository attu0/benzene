#include <chrono>
#include <memory>

#include <QApplication>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QKeyEvent>
#include <QCloseEvent>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

using namespace std::chrono_literals;


class TeleopWidget : public QWidget
{
public:
    explicit TeleopWidget(
        rclcpp::Node::SharedPtr node,
        QWidget *parent = nullptr)
        : QWidget(parent),
          node_(node)
    {
        publisher_ =
            node_->create_publisher<geometry_msgs::msg::TwistStamped>(
                "/diff_drive_controller/cmd_vel", 10);

        speed_ = 0.5;
        turn_ = 1.0;

        w_pressed_ = false;
        a_pressed_ = false;
        s_pressed_ = false;
        d_pressed_ = false;

        setWindowTitle("Benzene Teleop WASD");
        setFixedSize(450, 350);

        createGui();

        timer_ = node_->create_wall_timer(
            50ms,
            std::bind(
                &TeleopWidget::publishVelocity,
                this));

        setFocusPolicy(Qt::StrongFocus);
        setFocus();
    }

protected:

    void keyPressEvent(QKeyEvent *event) override
    {
        if (event->isAutoRepeat()) {
            return;
        }

        switch (event->key()) {
            case Qt::Key_W:
                w_pressed_ = true;
                break;

            case Qt::Key_A:
                a_pressed_ = true;
                break;

            case Qt::Key_S:
                s_pressed_ = true;
                break;

            case Qt::Key_D:
                d_pressed_ = true;
                break;

            case Qt::Key_Space:
                w_pressed_ = false;
                a_pressed_ = false;
                s_pressed_ = false;
                d_pressed_ = false;
                break;

            default:
                QWidget::keyPressEvent(event);
                break;
        }
    }


    void keyReleaseEvent(QKeyEvent *event) override
    {
        if (event->isAutoRepeat()) {
            return;
        }

        switch (event->key()) {
            case Qt::Key_W:
                w_pressed_ = false;
                break;

            case Qt::Key_A:
                a_pressed_ = false;
                break;

            case Qt::Key_S:
                s_pressed_ = false;
                break;

            case Qt::Key_D:
                d_pressed_ = false;
                break;

            default:
                QWidget::keyReleaseEvent(event);
                break;
        }
    }


    void closeEvent(QCloseEvent *event) override
    {
        publishStop();
        event->accept();
    }


private:

    void createGui()
    {
        auto *layout = new QVBoxLayout(this);

        auto *title =
            new QLabel("BENZENE ROBOT TELEOP");

        title->setAlignment(Qt::AlignCenter);

        QFont title_font;
        title_font.setPointSize(16);
        title_font.setBold(true);

        title->setFont(title_font);

        layout->addWidget(title);


        auto *instructions =
            new QLabel(
                "Click this window, then use WASD\n\n"
                "W       : Forward\n"
                "S       : Backward\n"
                "A       : Turn Left\n"
                "D       : Turn Right\n\n"
                "You can hold W+A, W+D, S+A, S+D simultaneously.\n"
                "SPACE   : Stop");

        instructions->setAlignment(Qt::AlignCenter);

        layout->addWidget(instructions);


        /* Speed */

        auto *speed_layout = new QHBoxLayout();

        auto *speed_label = new QLabel("Speed:");

        speed_slider_ = new QSlider(Qt::Horizontal);
        speed_slider_->setRange(1, 100);
        speed_slider_->setValue(50);

        speed_value_label_ =
            new QLabel("0.50 m/s");

        connect(
            speed_slider_,
            &QSlider::valueChanged,
            this,
            [this](int value)
            {
                speed_ = value / 100.0;

                speed_value_label_->setText(
                    QString::number(speed_, 'f', 2)
                    + " m/s");
            });

        speed_layout->addWidget(speed_label);
        speed_layout->addWidget(speed_slider_);
        speed_layout->addWidget(speed_value_label_);

        layout->addLayout(speed_layout);


        /* Turn */

        auto *turn_layout = new QHBoxLayout();

        auto *turn_label = new QLabel("Turn:");

        turn_slider_ = new QSlider(Qt::Horizontal);
        turn_slider_->setRange(1, 300);
        turn_slider_->setValue(100);

        turn_value_label_ =
            new QLabel("1.00 rad/s");

        connect(
            turn_slider_,
            &QSlider::valueChanged,
            this,
            [this](int value)
            {
                turn_ = value / 100.0;

                turn_value_label_->setText(
                    QString::number(turn_, 'f', 2)
                    + " rad/s");
            });

        turn_layout->addWidget(turn_label);
        turn_layout->addWidget(turn_slider_);
        turn_layout->addWidget(turn_value_label_);

        layout->addLayout(turn_layout);


        auto *status =
            new QLabel("STATUS: READY");

        status_label_ = status;

        status_label_->setAlignment(Qt::AlignCenter);

        layout->addWidget(status_label_);

        setLayout(layout);
    }


    void publishVelocity()
    {
        double linear = 0.0;
        double angular = 0.0;

        /*
         * Forward / backward
         */

        if (w_pressed_) {
            linear = speed_;
        }
        else if (s_pressed_) {
            linear = -speed_;
        }


        /*
         * Left / right
         */

        if (a_pressed_) {
            angular = turn_;
        }
        else if (d_pressed_) {
            angular = -turn_;
        }


        geometry_msgs::msg::TwistStamped msg;

        msg.header.stamp =
            node_->get_clock()->now();

        msg.header.frame_id = "base_link";

        msg.twist.linear.x = linear;
        msg.twist.linear.y = 0.0;
        msg.twist.linear.z = 0.0;

        msg.twist.angular.x = 0.0;
        msg.twist.angular.y = 0.0;
        msg.twist.angular.z = angular;

        publisher_->publish(msg);


        /*
         * GUI status
         */

        if (linear == 0.0 && angular == 0.0) {
            status_label_->setText("STATUS: STOPPED");
        }
        else {
            QString status = "STATUS: ";

            if (linear > 0.0) {
                status += "FORWARD ";
            }
            else if (linear < 0.0) {
                status += "BACKWARD ";
            }

            if (angular > 0.0) {
                status += "LEFT";
            }
            else if (angular < 0.0) {
                status += "RIGHT";
            }

            status_label_->setText(status);
        }
    }


    void publishStop()
    {
        geometry_msgs::msg::TwistStamped msg;

        msg.header.stamp =
            node_->get_clock()->now();

        msg.header.frame_id = "base_link";

        msg.twist.linear.x = 0.0;
        msg.twist.angular.z = 0.0;

        publisher_->publish(msg);
    }


    rclcpp::Node::SharedPtr node_;

    rclcpp::Publisher<
        geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;

    rclcpp::TimerBase::SharedPtr timer_;

    QSlider *speed_slider_;
    QSlider *turn_slider_;

    QLabel *speed_value_label_;
    QLabel *turn_value_label_;
    QLabel *status_label_;

    double speed_;
    double turn_;

    bool w_pressed_;
    bool a_pressed_;
    bool s_pressed_;
    bool d_pressed_;
};


int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);

    QApplication app(argc, argv);

    auto node =
        std::make_shared<rclcpp::Node>(
            "teleop_keyboard");

    auto widget =
        std::make_shared<TeleopWidget>(node);

    widget->show();

    RCLCPP_INFO(
        node->get_logger(),
        "Benzene GUI teleop started.");

    while (rclcpp::ok()) {
        rclcpp::spin_some(node);
        app.processEvents();
    }

    rclcpp::shutdown();

    return 0;
}