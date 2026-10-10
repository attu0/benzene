#!/bin/bash

# ============================================================
#                    BENZENE ROBOT
#              Autonomous Robot Startup
# ============================================================
# Hardware : Raspberry Pi 4B
# OS       : Ubuntu 24.04
# ROS      : ROS 2 Jazzy
# Workspace: ~/ros2_ws
# ============================================================

set -Eeuo pipefail

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

ROS_SETUP="/opt/ros/jazzy/setup.bash"
WORKSPACE_SETUP="$HOME/ros2_ws/install/setup.bash"

ROBOT_PACKAGE="benzene_bringup"
ROBOT_LAUNCH="benzene_robot.launch.py"

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ------------------------------------------------------------
# Benzene welcome banner
# ------------------------------------------------------------

if [[ -t 1 ]]; then
    clear || true
fi

printf '\033[0;36m'

if command -v figlet >/dev/null 2>&1; then
    figlet -c -f big "BENZENE"
else
    echo "BENZENE"
fi

printf '\033[0m'

echo "             AUTONOMOUS ROBOT PLATFORM"
echo "============================================================"

# ------------------------------------------------------------
# System information
# ------------------------------------------------------------

echo " Hostname       : $(hostname)"
echo " Username       : $(whoami)"
echo " IP Address     : $(hostname -I 2>/dev/null | awk '{print $1}')"
echo " Date           : $(date '+%d-%m-%Y %H:%M:%S')"
echo " Operating Sys. : Ubuntu 24.04"
echo " ROS Distro     : Jazzy"
echo " Workspace      : $HOME/ros2_ws"
echo "============================================================"

echo "                 SENSOR CONFIGURATION"
echo "------------------------------------------------------------"
echo " IMU            : ENABLED"
echo " Camera         : ENABLED"
echo " RPLIDAR        : ENABLED"
echo " Ultrasonic     : ENABLED"
echo "============================================================"

# ------------------------------------------------------------
# Verify ROS installation
# ------------------------------------------------------------

if [[ ! -f "$ROS_SETUP" ]]; then
    log "ERROR: ROS 2 setup file not found: $ROS_SETUP"
    exit 1
fi

# ------------------------------------------------------------
# Source ROS 2 Jazzy
# ------------------------------------------------------------

log "Loading ROS 2 Jazzy environment..."

source "$ROS_SETUP"

# ------------------------------------------------------------
# Source Benzene workspace
# ------------------------------------------------------------

if [[ ! -f "$WORKSPACE_SETUP" ]]; then
    log "ERROR: Workspace setup file not found: $WORKSPACE_SETUP"
    log "Build the workspace before starting Benzene."
    exit 1
fi

log "Loading Benzene workspace..."

source "$WORKSPACE_SETUP"

# ------------------------------------------------------------
# Verify Benzene bringup package
# ------------------------------------------------------------

if ! ros2 pkg prefix "$ROBOT_PACKAGE" >/dev/null 2>&1; then
    log "ERROR: Package '$ROBOT_PACKAGE' is not available."
    log "Check the workspace build and installation."
    exit 1
fi

log "ROS 2 environment loaded successfully."
log "Benzene bringup package verified."

# ------------------------------------------------------------
# Start Benzene robot and sensors
# ------------------------------------------------------------

echo
printf '\033[1;32m'
echo "============================================================"
echo "               STARTING BENZENE ROBOT"
echo "============================================================"
printf '\033[0m'

log "Launching robot and sensors..."
log "IMU, camera, RPLIDAR and ultrasonic are enabled."
echo

exec ros2 launch "$ROBOT_PACKAGE" "$ROBOT_LAUNCH" \
    include_imu:=true \
    include_camera:=true \
    include_rplidar:=true \
    include_ultrasonic:=true