# Benzene Bringup

## Overview

The `benzene_bringup` package provides launch files and scripts for starting and configuring the Benzene robot system using ROS 2.

It serves as an entry point for bringing up the robot's software components and coordinating their startup.

## Package Structure

| Directory | Purpose |
|---|---|
| `launch/` | ROS 2 launch files for starting robot components |
| `scripts/` | Helper scripts used during robot startup and operation |

## Requirements

- ROS 2 Jazzy
- The Benzene ROS 2 workspace
- Dependencies required by the selected launch file
- Hardware and device permissions when running with the physical robot

## Installation and Build

From the root of the workspace:

```bash
cd ~/benzene
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Run `rosdep install` from the appropriate workspace source directory if your workspace has a different layout.

## Usage

Source ROS 2 and the workspace before running launch files:

```bash
source /opt/ros/jazzy/setup.bash
source ~/benzene/install/setup.bash
```

List the available launch files:

```bash
ros2 pkg prefix benzene_bringup
```

Inspect the package's `launch/` directory to identify the supported launch files and their required arguments.

Launch the appropriate file using:

```bash
ros2 launch benzene_bringup <launch_file_name>
```

Replace `<launch_file_name>` with the actual launch filename, including the `.launch.py` extension.

## Helper Scripts

The `scripts/` directory contains supporting scripts for robot startup and operation.

Refer to each script's documentation and source code for its purpose, required arguments, and execution instructions.

## Troubleshooting

| Problem | Suggested action |
|---|---|
| Package not found | Source the ROS 2 installation and workspace setup files |
| Launch file not found | Check the filename and confirm that it is installed by the package |
| Missing dependencies | Run `rosdep install` and rebuild the workspace |
| Hardware access errors | Check device paths and Linux permissions |
| A node fails to start | Inspect its terminal output and verify its configuration |

## Related Packages

- `benzene_description` — robot description and model configuration.
- `benzene_hardware` — physical hardware integration.
- `benzene_control` — robot control functionality.
- `benzene_navigation` — navigation configuration and launch files.
- `benzene_gazebo` — simulation resources.

Refer to the main [Benzene README](../README.md) for overall project setup.

## License

See the repository's [LICENSE](../LICENSE) file.
