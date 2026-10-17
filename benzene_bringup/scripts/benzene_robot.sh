#!/bin/bash
# Real benzene robot bringup (run on the Pi) with toggleable peripherals.
#
# Everything is ON by default. Pass words to switch things off/on:
#
#   ./benzene_robot.sh                      # base + lidar, imu, camera, ultrasonic
#   ./benzene_robot.sh nolidar              # everything except RPLIDAR
#   ./benzene_robot.sh nocam noultra        # drop camera and ultrasonic
#   ./benzene_robot.sh bare                 # drive base only, no sensors
#   ./benzene_robot.sh bare lidar imu       # base + only lidar and imu
#   ./benzene_robot.sh joy                  # add joystick teleop
#   ./benzene_robot.sh rviz                 # add RViz (only if the Pi has a display)
#
# Words (processed left to right, so order matters with "bare"):
#   lidar  / nolidar
#   imu    / noimu
#   cam    / nocam
#   ultra  / noultra
#   bare   -> turn all four sensors off
#   all    -> turn all four sensors on
#   joy    -> use_joy:=true
#   rviz   -> use_rviz:=true

LIDAR=true
IMU=true
CAM=true
ULTRA=true
JOY=false
RVIZ=false

for arg in "$@"; do
    case "$arg" in
        lidar)   LIDAR=true ;;
        nolidar) LIDAR=false ;;
        imu)     IMU=true ;;
        noimu)   IMU=false ;;
        cam)     CAM=true ;;
        nocam)   CAM=false ;;
        ultra)   ULTRA=true ;;
        noultra) ULTRA=false ;;
        bare)    LIDAR=false; IMU=false; CAM=false; ULTRA=false ;;
        all)     LIDAR=true;  IMU=true;  CAM=true;  ULTRA=true ;;
        joy)     JOY=true ;;
        rviz)    RVIZ=true ;;
        -h|--help|help)
            sed -n '2,25p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Try: lidar nolidar imu noimu cam nocam ultra noultra bare all joy rviz"
            exit 1
            ;;
    esac
done

# Source ROS + workspace if not already sourced in this shell
if ! command -v ros2 >/dev/null 2>&1; then
    source /opt/ros/jazzy/setup.bash
fi
if ! ros2 pkg prefix benzene_bringup >/dev/null 2>&1; then
    source "$HOME/ros2_ws/install/setup.bash"
fi

echo "============================================================"
echo "  BENZENE REAL ROBOT"
echo "------------------------------------------------------------"
echo "  RPLIDAR    : $LIDAR"
echo "  IMU        : $IMU"
echo "  Camera     : $CAM"
echo "  Ultrasonic : $ULTRA"
echo "  Joystick   : $JOY"
echo "  RViz       : $RVIZ"
echo "============================================================"
echo "Launching Benzene (Ctrl-C to stop)..."

# Run in the foreground (no '&' / pkill): Ctrl-C reaches ros2 launch directly,
# which shuts every node down cleanly (RPLIDAR motor stop, Arduino serial close).
ros2 launch benzene_bringup benzene_robot.launch.py \
    include_rplidar:=$LIDAR \
    include_imu:=$IMU \
    include_camera:=$CAM \
    include_ultrasonic:=$ULTRA \
    use_joy:=$JOY \
    use_rviz:=$RVIZ