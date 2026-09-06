# Benzene
A simple diff drive bot that is made by undergrads as their final year project

This is an Simple Differential Drive robot named benzene, using ros2 jazzy following some industrial standards complete heavy duty laser cut metal built in college labs.

ROS 2 Distro | Branch
:----------: | :----:
**Jazzy** | [`jazzy`](../../tree/jazzy)

## Package Summary

- [`benzen_arduino`](./benzene_arduino/): Contains code that is used on the Arduino also some test code to configure your real bot
- [`benzen_bringup`](./benzene_bringup/): Contains all the launch files and the scripts to easy lauch
- [`benzen_control`](./benzene_control/): Have the real bot config params
- [`benzen_description`](./benzene_description/): Contains the bot urdf meshes etc
- [`benzen_docking`](./benzene_docking/): Contains code for the docking action
- [`benzen_explore`](./benzene_explore/): Contains the launch code for the auto explore using explore lite
- [`benzen_explore_msgs`](./benzene_explore_msgs/): Supporting files for the explore lite
- [`benzen_gazebo`](./benzene_gazebo/): Contains the gazebo simulation along with different worlds and model files
- [`benzen_hardware`](./benzene_hardware/): Contins the Hardware interface code to connect arduino to ros2 control
- [`benzen_imu`](./benzene_imu/): Contains the code to launch and start the imu connected to the pi
- [`benzen_localization`](./benzene_localization/): Contains sensor fusion code ekf ans kalman fillter
- [`benzen_msgs`](./benzene_msgs/): Contains some demo action cmds
- [`benzen_navigation`](./benzene_navigation/): Contians the slam and nave params and launch files
- [`benzen_serial`](./benzene_serial/): This is responsibele to build serial communication between arduino and the pi
- [`benzen_system_tests`](./benzene_system_tests/): Contains some test code for the bot
- [`docker`](./docker/): Have docker file to work with

## Features

What are the features that we added to this project are :

- **Differential Drive**
- **Sensor Fusion**
- **Gazebo Simulation**
- **Sim-To-Real**
- **Self Explore**
- **Slam**
- **Nav2**

#### colcon workspace

Packages here provided are colcon packages. As such a colcon workspace is expected:

1. Create colcon workspace

```
mkdir -p ~/ros2_ws/src
```

2. Clone this repository in the `src` folder

```
cd ~/ros2_ws/src
```

```
git clone https://github.com/Ekumen-OS/andino.git
```

3. Install dependencies via `rosdep`

```
cd ~/ros2_ws
```

```
rosdep install --from-paths src --ignore-src -i -y
```

4. Build the packages

```
colcon build
```

5. Finally, source the built packages
   If using `bash`:

```
source install/setup.bash
```

### Simulated Robot

**Terminal: Start Gazebo, Rviz**
```bash
ros2 launch benzene_gazebo benzene.gazebo.launch.py \
    enable_odom_tf:=true \
    headless:=False \
    load_controllers:=true \
    world_file:=warehouse.sdf \ #try cafe.world
    use_rviz:=true \
    use_robot_state_pub:=true \
    use_sim_time:=true \
    x:=0.0 \
    y:=0.0 \
    z:=0.20 \
    roll:=0.0 \
    pitch:=0.0 \
    yaw:=0.0 &
```

**Terminal: Start Gazebo, Rviz, with slam** (same commands as physical robot, add `sim:=true`):
```bash
ros2 launch benzene_bringup benzene_navigation.launch.py \
    enable_odom_tf:=false \
    headless:=False \
    load_controllers:=true \
    slam:=True \
    map:=/home/atharv/ros2_ws/src/benzene/benzene_navigation/maps/cafe_world_map.yaml \ #try warehouse_world_map.yaml
    use_rviz:=true \
    use_robot_state_pub:=true \
    use_sim_time:=true \
    x:=0.0 \
    y:=0.0 \
    z:=0.20 \
    roll:=0.0 \
    pitch:=0.0 \
    yaw:=0.0 \
    world_file:=cafe.world & #try warehouse.sdf
```

**Launch using bash**
```bash
chmod +x ~/ros2_ws/srcbenzene_bringup/scripts/*
~/ros2_ws/src/benzen/benzene_bringup/scripts/benzene_gazebo.sh # for gazebo
~/ros2_ws/src/benzen/benzene_bringup/scripts/benzene_navigation.sh # for nav use args eg : ./benzene_navigation.sh slam(for slam) cafe(for cafe)
```

