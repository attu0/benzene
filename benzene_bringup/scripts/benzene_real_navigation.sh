#!/bin/bash
# Real benzene robot: SLAM or Nav2. Run on the LAPTOP.
#
#   On the Pi first:
#     ros2 launch benzene_bringup benzene_robot.launch.py include_rplidar:=true
#
#   Then here:
#     ./benzene_real_navigation.sh slam                 # build a map
#     ./benzene_real_navigation.sh /path/to/map.yaml    # navigate on a saved map
#
#   Save the map while SLAM is running (second terminal):
#     ros2 run nav2_map_server map_saver_cli -f ~/maps/lab

if [ -z "$1" ]; then
    echo "Usage: $0 slam | /path/to/map.yaml"
    exit 1
fi

if [ "$1" = "slam" ]; then
    ARGS="slam:=True"
else
    if [ ! -f "$1" ]; then
        echo "Map file not found: $1"
        exit 1
    fi
    ARGS="slam:=False map:=$1"
fi

echo "Launching Nav2 for the real robot ($ARGS)..."
ros2 launch benzene_bringup benzene_real_navigation.launch.py $ARGS &
LAUNCH_PID=$!

# Ctrl-C: ask the launch to shut down cleanly (no pkill of unrelated ROS processes).
cleanup() {
    echo "Shutting down..."
    kill -INT "$LAUNCH_PID" 2>/dev/null
    wait "$LAUNCH_PID" 2>/dev/null
}
trap cleanup SIGINT SIGTERM

wait "$LAUNCH_PID"