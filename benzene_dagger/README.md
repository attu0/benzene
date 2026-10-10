# Benzene DAgger

## Overview

The `benzene_dagger` package is used for robot simulation, expert data collection, and behavioral cloning. It helps train a robot to perform tasks by learning from expert demonstrations.

## Features

- Simulates the robot in Gazebo.
- Visualizes the robot in RViz.
- Collects expert demonstration data.
- Trains a behavioral cloning model.
- Runs a learned CNN-based controller.

## Requirements

- ROS 2 Jazzy
- Gazebo and RViz
- `benzene_bringup`
- Python 3 and the required machine-learning dependencies
- The Benzene workspace built successfully

## Build

Open a terminal and run:

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select benzene_dagger --symlink-install
source install/setup.bash
```

## 1. Run the Simulation and Teleoperation

First, launch the simulation:

```bash
ros2 launch benzene_dagger dagger_sim.launch.py
```

This launches Gazebo, RViz, and the scan marker, according to the launch configuration.

Open a second terminal and run keyboard teleoperation:

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run benzene_bringup teleop_keyboard
```

Use the keyboard controls configured by the teleoperation node to move the robot.

## 2. Collect Expert Data

Run the data collection launch file:

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch benzene_dagger data_collection.launch.py
```

**Important:** This launch file includes the simulation. Do not launch `dagger_sim.launch.py` separately while collecting data.

Use the expert teleoperation controls as required by the setup and save the demonstration episodes.

## 3. Train the Behavioral Cloning Model

Open the training script:

```text
benzene_dagger/scripts/train_behavioral_cloning.py
```

Find the `DATASET_DIR` setting and update it to the folder containing your newly collected episode data.

The current script uses this example episode:

```text
episode_20260926_163735
```

Change it to your actual dataset folder before training.

Run the training script:

```bash
cd ~/ros2_ws
python3 ~/ros2_ws/src/benzene/benzene_dagger/scripts/train_behavioral_cloning.py
```

Training time depends on the dataset size and your computer's hardware.

## 4. Run the Learned Policy

First, launch the simulation in one terminal:

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch benzene_dagger dagger_sim.launch.py
```

Open a second terminal and run the learned controller:

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 ~/ros2_ws/src/benzene/benzene_dagger/scripts/cnn_controller.py --ros-args -p use_sim_time:=true
```

The controller uses simulation time and runs the learned policy according to the script's implementation.

## Troubleshooting

- **Package not found:** Build the package and source `install/setup.bash`.
- **Launch file not found:** Check that the launch file exists in `benzene_dagger/launch/`.
- **Dataset not found:** Verify the `DATASET_DIR` path in the training script.
- **Python dependency errors:** Install the dependencies required by the training and controller scripts.
- **Robot does not move:** Check that the simulation is running and that the controller's ROS topics match the robot's topics.

## Related Packages

- `benzene_bringup` — robot bringup and keyboard teleoperation.
- `benzene_gazebo` — simulation assets and worlds.
- `benzene_control` — robot control functionality.

