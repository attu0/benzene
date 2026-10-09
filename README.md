# Benzene 🤖

### An Autonomous Differential-Drive Robot Built by Undergraduates

**Benzene** is an autonomous differential-drive mobile robot developed by undergraduate students as a final-year engineering project. Built using heavy-duty, laser-cut metal components manufactured in our college laboratory, Benzene combines robotics software, embedded systems, sensor integration, and autonomous navigation using **ROS 2 Jazzy**.

The project follows a modular architecture inspired by industrial robotics practices, with separate packages for hardware integration, robot description, control, localization, simulation, navigation, and autonomous exploration.

Our goal is to build a reliable, extensible mobile robotics platform that supports simulation, real-world deployment, and further experimentation with autonomous robotics.

<p align="center">
  <img src="media/benzene.jpg" alt="Benzene autonomous mobile robot" width="600">
</p>

> **ROS 2 Distribution:** Jazzy
> **Primary Platform:** Ubuntu 24.04 LTS
> **Robot Type:** Differential Drive
> **Simulation:** Gazebo
> **Visualization:** RViz2
> **Repository:** [attu0/benzene](https://github.com/attu0/benzene)

---

## 📌 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Package Overview](#-package-overview)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Building the Workspace](#-building-the-workspace)
- [Running the Simulation](#-running-the-simulation)
- [SLAM and Autonomous Navigation](#-slam-and-autonomous-navigation)
- [Launching with Helper Scripts](#-launching-with-helper-scripts)
- [Physical Robot Setup](#-physical-robot-setup)
- [Project Structure](#-project-structure)
- [Future Development](#-future-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Features

Benzene integrates multiple robotics technologies into a unified ROS 2 ecosystem.

### 1. Differential Drive
A two-wheel differential-drive platform with wheel odometry and velocity control.

### 2. Sensor Fusion
Integrates sensor data and robot motion estimates to improve localization and state estimation using an Extended Kalman Filter (EKF).

### 3. Gazebo Simulation
Simulates the robot in virtual environments for development, testing, and validation before deploying changes to the physical robot.

### 4. Simulation-to-Reality (Sim-to-Real)
Uses a common ROS 2 software architecture for simulation and physical hardware, reducing the effort required to transfer and test robotics functionality.

### 5. Simultaneous Localization and Mapping (SLAM)
Uses SLAM Toolbox to construct maps of unknown environments while estimating the robot's position.

### 6. Autonomous Navigation
Integrates Nav2 to support autonomous movement toward target poses using mapping or an existing map, localization, planning, and obstacle avoidance.

### 7. Autonomous Exploration
Integrates exploration functionality to identify and navigate toward unexplored regions of an environment.

### 8. Hardware Integration
Connects the robot's embedded controller to ROS 2 through a hardware interface and serial communication.

### 9. Modular ROS 2 Architecture
Organizes functionality into independent packages to simplify development, debugging, testing, and future expansion.

---

## 🏗️ System Architecture

Benzene uses ROS 2 as the communication layer between its hardware, control, sensing, and navigation components.

```text
                       ┌────────────────────────┐
                       │       ROS 2 Jazzy      │
                       │                        │
                       │   Robot Applications   │
                       └───────────┬────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
          ┌────────────┐    ┌────────────┐    ┌────────────┐
          │   Control  │    │ Localization│   │ Navigation │
          │ ros2_control│   │    EKF      │    │    Nav2    │
          └──────┬─────┘    └──────┬─────┘    └──────┬─────┘
                 │                 ▲                 │
                 ▼                 │                 ▼
          ┌────────────────────────────────────────────────┐
          │                 Robot Hardware                 │
          │                                                │
          │  Motors │ Encoders │ IMU │ LiDAR │ Other Sensors│
          └────────────────────────────────────────────────┘
```

The architecture supports two primary operating modes:

- **Simulation:** Robot model, sensors, and environment run in Gazebo.
- **Physical robot:** ROS 2 communicates with the actual robot hardware through the hardware interface and embedded controller.

---

## 📦 Package Overview

The repository is organized into modular ROS 2 packages.

| Package | Description |
|---|---|
| [`benzene_arduino`](./benzene_arduino/) | Embedded controller code and hardware testing utilities. |
| [`benzene_bringup`](./benzene_bringup/) | Launch files and scripts for starting robot components and complete robot configurations. |
| [`benzene_control`](./benzene_control/) | Robot control configuration, including controller parameters. |
| [`benzene_description`](./benzene_description/) | Robot URDF/Xacro descriptions, meshes, and other model resources. |
| [`benzene_docking`](./benzene_docking/) | Docking-related functionality and actions. |
| [`benzene_explore`](./benzene_explore/) | Autonomous exploration functionality. |
| [`benzene_explore_msgs`](./benzene_explore_msgs/) | Custom messages and supporting interfaces for exploration. |
| [`benzene_gazebo`](./benzene_gazebo/) | Gazebo simulation launch files, worlds, models, and simulation resources. |
| [`benzene_hardware`](./benzene_hardware/) | ROS 2 hardware interface connecting robot hardware to the control framework. |
| [`benzene_imu`](./benzene_imu/) | IMU driver integration and launch/configuration files. |
| [`benzene_localization`](./benzene_localization/) | Localization and sensor-fusion configuration, including EKF parameters. |
| [`benzene_msgs`](./benzene_msgs/) | Custom ROS 2 interfaces and demonstration action definitions. |
| [`benzene_navigation`](./benzene_navigation/) | SLAM, Nav2 configuration, maps, and navigation launch files. |
| [`benzene_serial`](./benzene_serial/) | Serial communication support between the embedded controller and the main computer. |
| [`benzene_camera`](./benzene_camera/) | Camera integration. |
| [`benzene_ultrasonic`](./benzene_ultrasonic/) | Ultrasonic sensor integration. |
| [`benzene_dagger`](./benzene_dagger/) | Behavioral cloning and imitation-learning development for the robot. |
| [`benzene_system_tests`](./benzene_system_tests/) | System-level testing utilities. |
| [`docker`](./docker/) | Docker configuration for supported development workflows. |

> **Note:** Package directories and optional components may change as development progresses. Refer to the repository for the current implementation.

---

## 🛠️ Requirements

### Software

| Component | Requirement |
|---|---|
| Operating System | Ubuntu 24.04 LTS |
| Robotics Middleware | ROS 2 Jazzy |
| Build System | colcon |
| Dependency Management | rosdep |
| Visualization | RViz2 |
| Simulation | Gazebo |
| Navigation | Nav2 |
| Mapping | SLAM Toolbox |
| Robot Control | ros2_control |

### Hardware

The physical robot may include the following components:

- Differential-drive chassis.
- Two geared DC motors with encoders.
- Motor driver.
- Embedded motor controller.
- Raspberry Pi or another supported Linux computer.
- IMU for orientation and motion sensing.
- LiDAR for mapping and navigation.
- Camera and ultrasonic sensors for additional perception capabilities.
- Battery and voltage regulation circuitry.

The exact hardware configuration depends on the robot's current build.

---

## 📥 Installation

### 1. Create a ROS 2 workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### 2. Clone the repository

```bash
git clone https://github.com/attu0/benzene.git
```

### 3. Install ROS 2 dependencies

Ensure that ROS 2 Jazzy and `rosdep` are installed and configured.

```bash
sudo apt update
sudo apt install python3-rosdep python3-colcon-common-extensions
```

Initialize `rosdep` if it has not already been initialized:

```bash
sudo rosdep init
rosdep update
```

If `rosdep` is already initialized, run only:

```bash
rosdep update
```

Install the dependencies declared by the repository's package manifests:

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash

rosdep install \
  --from-paths src \
  --ignore-src \
  --rosdistro jazzy \
  -r -y
```


## 📦 Installing Dependencies

Benzene provides a dependency installation script, `requirements.sh`, to simplify setting up the development environment.

The script checks for required ROS 2 packages, system libraries, Python dependencies, and build tools. It installs missing packages using APT.

### Prerequisites

- Ubuntu 24.04 LTS
- ROS 2 Jazzy (the script can attempt to configure the ROS 2 repository if it is not installed)
- Internet connection
- Sudo privileges

### 1. Navigate to the repository

```bash
cd ~/ros2_ws/src/benzene

---

## 🔨 Building the Workspace

Build the complete workspace:

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install
```

If you want to build a specific package and its dependencies:

```bash
colcon build --symlink-install \
  --packages-up-to benzene_bringup
```

Source the workspace after a successful build:

```bash
source ~/ros2_ws/install/setup.bash
```

To make the ROS 2 environment available in new Bash terminals, add the following to `~/.bashrc`:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

Reload the configuration:

```bash
source ~/.bashrc
```

Verify that ROS 2 can discover the Benzene packages:

```bash
ros2 pkg list | grep benzene
```

## 🌎 Gazebo Simulation, SLAM & Nav2

Benzene provides helper scripts to simplify launching Gazebo simulations and testing autonomous navigation using ROS 2 Jazzy.

The project includes two main scripts:

- `benzene_gazebo.sh` — launches the robot in a Gazebo simulation.
- `benzene_navigation.sh` — launches Gazebo with the navigation stack, supporting both SLAM and map-based navigation.

Both scripts support selecting an environment.

### Available Environments

| Environment | Gazebo World | Map |
|---|---|---|
| Cafe | `cafe.world` | `cafe_world_map.yaml` |
| Office | `husarion_office.sdf` | `office_world_map.yaml` |
| Warehouse (default) | `warehouse.sdf` | `warehouse_world_map.yaml` |

The map files are located in:

```text
benzene_navigation/maps/


---

## 🌍 Running the Simulation

Benzene provides a Gazebo simulation environment for testing robot behavior without requiring the physical robot.

### Launch Gazebo and RViz2

First, source the workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

Launch the robot in the warehouse environment:

```bash
ros2 launch benzene_gazebo benzene.gazebo.launch.py \
  enable_odom_tf:=true \
  headless:=False \
  load_controllers:=true \
  world_file:=warehouse.sdf \
  use_rviz:=true \
  use_robot_state_pub:=true \
  use_sim_time:=true \
  x:=0.0 \
  y:=0.0 \
  z:=0.20 \
  roll:=0.0 \
  pitch:=0.0 \
  yaw:=0.0
```

**Available configuration options may include:**

| Argument | Purpose |
|---|---|
| `enable_odom_tf` | Enables or disables the odometry-to-base transform. |
| `headless` | Controls whether the simulation runs without its graphical interface. |
| `load_controllers` | Controls the loading of robot controllers. |
| `world_file` | Specifies the simulation world. |
| `use_rviz` | Enables RViz2 visualization. |
| `use_robot_state_pub` | Enables robot state publishing. |
| `use_sim_time` | Uses simulation time instead of wall-clock time. |
| `x`, `y`, `z` | Initial robot position. |
| `roll`, `pitch`, `yaw` | Initial robot orientation. |

Other available worlds may include the cafe environment, depending on the files currently present in `benzene_gazebo`.

For example, to use a cafe world, change the world argument to the corresponding world filename supported by the launch file.

---

## 🗺️ SLAM and Autonomous Navigation

Benzene integrates SLAM Toolbox and Nav2 for mapping and autonomous navigation.

### Launch the navigation stack in simulation

Start the navigation launch file with simulation enabled:

```bash
ros2 launch benzene_bringup benzene_navigation.launch.py \
  enable_odom_tf:=false \
  headless:=False \
  load_controllers:=true \
  slam:=True \
  use_rviz:=true \
  use_robot_state_pub:=true \
  use_sim_time:=true \
  x:=0.0 \
  y:=0.0 \
  z:=0.20 \
  roll:=0.0 \
  pitch:=0.0 \
  yaw:=0.0 \
  world_file:=cafe.world \
  sim:=true
```

This configuration is intended to start the robot's navigation workflow in simulation with SLAM enabled.

> **Important:** The launch file must support the arguments supplied above. Check `benzene_navigation.launch.py` for the exact argument names and defaults in the current branch. In particular, verify the supported world filename and whether the simulation argument is named `sim` or `use_sim_time`.

### Mapping a new environment

With SLAM enabled:

1. Start the simulation or physical robot.
2. Confirm that the LiDAR publishes scan data.
3. Verify that the robot's odometry and TF transforms are available.
4. Start SLAM Toolbox through the appropriate launch configuration.
5. Drive the robot through the environment.
6. Monitor the map in RViz2.
7. Save the completed map using the ROS 2 map-saving tools.

For example:

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ~/benzene_map
```

This saves the map to files such as `benzene_map.yaml` and `benzene_map.pgm`.

### Autonomous navigation using a saved map

To navigate using a previously saved map, configure the navigation stack to load the appropriate map and use a compatible localization configuration.

The map file should be supplied through the map argument supported by the relevant launch file.

In RViz2, configure the initial pose when required, set a navigation goal, and monitor the robot's progress.

---

## 🖥️ Launching with Helper Scripts

Benzene includes helper scripts intended to simplify common launch operations.

Make the scripts executable:

```bash
chmod +x ~/ros2_ws/src/benzene/benzene_bringup/scripts/*
```

Launch the Gazebo simulation using the helper script:

```bash
~/ros2_ws/src/benzene/benzene_bringup/scripts/benzene_gazebo.sh
```

Launch the navigation workflow:

```bash
~/ros2_ws/src/benzene/benzene_bringup/scripts/benzene_navigation.sh
```

If the navigation script supports command-line arguments, use the options implemented by that script. For example, the intended workflow may support selecting SLAM or a particular world:

```bash
./benzene_navigation.sh slam
```

or:

```bash
./benzene_navigation.sh cafe
```

Check the script's argument-handling code before relying on these examples.

---

## 🔌 Physical Robot Setup

Benzene is designed to support deployment on a physical differential-drive robot.

The hardware workflow connects the motor controller, encoders, and sensors to ROS 2 through the relevant hardware and sensor packages.

### General workflow

1. Connect the robot's motor controller and sensors.
2. Verify the embedded controller firmware and communication interface.
3. Configure the serial device and communication parameters.
4. Confirm that the hardware interface loads successfully.
5. Start the robot's sensor drivers.
6. Verify encoder-based odometry and IMU data.
7. Start the localization and navigation stack.
8. Test movement at low speed in a clear environment before enabling autonomous operation.

### Verify ROS 2 communication

After launching the physical robot, inspect the available topics:

```bash
ros2 topic list
```

Check the command velocity topic:

```bash
ros2 topic info /cmd_vel
```

Inspect odometry:

```bash
ros2 topic echo /odom
```

Inspect IMU data if the corresponding driver is running:

```bash
ros2 topic echo /imu/data
```

Inspect LiDAR data if a LiDAR driver is running:

```bash
ros2 topic echo /scan
```

Topic names may vary according to the active configuration.

> **Safety:** Test motor direction, emergency stopping, sensor operation, and velocity limits before running autonomous navigation on the physical robot. Keep the robot's wheels clear of obstacles during initial motor tests.

---

## 📁 Project Structure

The repository follows a modular ROS 2 workspace layout.

```text
benzene/
├── benzene_arduino/
├── benzene_bringup/
│   ├── launch/
│   └── scripts/
├── benzene_camera/
├── benzene_control/
├── benzene_dagger/
├── benzene_description/
├── benzene_docking/
├── benzene_explore/
├── benzene_explore_msgs/
├── benzene_gazebo/
│   ├── launch/
│   ├── models/
│   └── worlds/
├── benzene_hardware/
├── benzene_imu/
├── benzene_localization/
├── benzene_msgs/
├── benzene_navigation/
│   ├── config/
│   ├── launch/
│   └── maps/
├── benzene_serial/
├── benzene_system_tests/
├── benzene_ultrasonic/
├── docker/
└── README.md
```

This is a logical overview of the main components rather than a guaranteed exhaustive listing of every directory.

---

## 🔬 Future Development

Benzene is an ongoing robotics project. Potential areas for further development include:

- Improved wheel odometry and sensor-fusion accuracy.
- More robust autonomous exploration.
- Better obstacle detection and avoidance.
- Camera-based perception and visual navigation.
- Battery monitoring and power-management integration.
- Automated docking and charging.
- Imitation learning and behavioral cloning.
- DAgger-based data collection and policy improvement.
- Expanded simulation testing and hardware validation.
- Improved system-level testing and deployment tools.

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Ensure that the affected packages build successfully.
5. Submit a pull request describing your changes.

```bash
git clone https://github.com/attu0/benzene.git

cd benzene

git checkout -b feature/your-feature
```

For changes involving ROS 2 packages, validate the relevant build and runtime behavior before submitting a pull request.

---

## 📄 License

Please refer to the repository's `LICENSE` file for licensing information.

---

## 👨‍💻 Project

**Benzene — Autonomous Differential-Drive Robotics Platform**

Developed by undergraduate students as a final-year engineering project.

**Repository:** [https://github.com/attu0/benzene](https://github.com/attu0/benzene)

**ROS 2 Distribution:** Jazzy

**Focus Areas:** Mobile Robotics · ROS 2 · SLAM · Navigation · Sensor Fusion · Gazebo · Embedded Systems