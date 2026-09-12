#!/bin/bash
cleanup() {
    echo "Cleaning up..."
    sleep 5.0
    pkill -9 -f "ros2|gazebo|gz|nav2|amcl|bt_navigator|nav_to_pose|rviz2|assisted_teleop|cmd_vel_relay|robot_state_publisher|joint_state_publisher|move_to_free|mqtt|autodock|cliff_detection|moveit|move_group|basic_navigator"

}
# Set up cleanup trap
trap 'cleanup' SIGINT SIGTERM
# SLAM
if [ "$1" = "slam" ]; then
    SLAM_ARG="slam:=True"
    WORLD="$2"
else
    SLAM_ARG="slam:=False"
    WORLD="$1"
fi
# World
if [ "$WORLD" = "cafe" ]; then
    WORLD_ARG="world_file:=cafe.world"
    MAP_ARG="map:=/home/atharv/ros2_ws/src/benzene/benzene_navigation/maps/cafe_world_map.yaml"
else
    WORLD_ARG="world_file:=warehouse.sdf"
    MAP_ARG="map:=/home/atharv/ros2_ws/src/benzene/benzene_navigation/maps/warehouse_world_map.yaml"
fi
export GZ_SIM_RESOURCE_PATH=~/ros2_ws/install/benzene_description/share/
echo "Launching Gazebo simulation with Nav2..."
ros2 launch benzene_bringup benzene_navigation.launch.py \
    enable_odom_tf:=false \
    headless:=False \
    load_controllers:=true \
    $WORLD_ARG \
    $MAP_ARG \
    use_rviz:=true \
    use_robot_state_pub:=true \
    use_sim_time:=true \
    x:=0.0 \
    y:=0.0 \
    z:=0.20 \
    roll:=0.0 \
    pitch:=0.0 \
    yaw:=0.0 \
    "$SLAM_ARG" &

echo "Waiting 25 seconds for simulation to initialize..."
sleep 25
echo "Adjusting camera position..."
gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 2000 --req "pose: {position: {x: 0.0, y: -2.0, z: 2.0} orientation: {x: -0.2706, y: 0.2706, z: 0.6533, w: 0.6533}}"
wait