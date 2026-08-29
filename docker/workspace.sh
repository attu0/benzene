#!/bin/bash
set -e

# ============================================================
# Benzene Diff-Drive Robot Workspace Setup
# ============================================================

ROS_DISTRO="jazzy"

echo "=========================================="
echo " Setting up ROS 2 $ROS_DISTRO workspace"
echo "=========================================="

# Source ROS 2
source /opt/ros/$ROS_DISTRO/setup.bash

# ------------------------------------------------------------
# ROS 2 workspace
# ------------------------------------------------------------

ROS_WS="/root/ros2_ws"

cd "$ROS_WS"

echo "=========================================="
echo " Installing ROS 2 dependencies"
echo "=========================================="

apt-get update

rosdep update

# Installs whatever benzene_* packages declare in their package.xml
# (e.g. serial, gazebo, nav2, robot_localization deps) so you don't
# have to hand-maintain a system package list here.
rosdep install \
    -i \
    --from-path src \
    --rosdistro "$ROS_DISTRO" \
    -y

echo "All required rosdeps installed successfully."

# ------------------------------------------------------------
# Build workspace
# ------------------------------------------------------------

echo "=========================================="
echo " Building ROS 2 workspace"
echo "=========================================="

cd "$ROS_WS"

colcon build --symlink-install

# Source newly built workspace
source "$ROS_WS/install/setup.bash"

echo "=========================================="
echo " Workspace setup completed successfully"
echo "=========================================="