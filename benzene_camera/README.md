# Benzene Camera

## Overview

The `benzene_camera` package provides a ROS 2 camera node based on **libcamera**. It supports compatible V4L2 cameras and Raspberry Pi camera modules.

The node captures images and publishes them as ROS 2 image messages. It also publishes camera calibration information and provides a service for updating camera parameters.

## Features

- Camera support through libcamera
- Raw and compressed image topics
- Camera information publishing
- Runtime camera control parameters
- Camera orientation and resolution configuration
- Camera calibration support
- Integration with the ROS 2 image pipeline

## Requirements

- ROS 2 Jazzy
- A camera supported by the installed libcamera version
- libcamera version 0.1 or later
- Required ROS 2 dependencies, including sensor message interfaces

**Note:** Raspberry Pi camera support depends on the installed libcamera version. Some newer camera modules may require the Raspberry Pi libcamera fork.

## Installation

Source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Install the available ROS camera package if it is provided for your distribution:

```bash
sudo apt update
sudo apt install ros-jazzy-camera-ros
```

For a source build, make sure the `benzene_camera` package and its dependencies are present in the workspace. Install dependencies and build:

```bash
cd ~/benzene
rosdep install --from-paths . --ignore-src -r -y
colcon build --packages-up-to benzene_camera --symlink-install
source install/setup.bash
```

If the workspace uses a custom libcamera installation, follow the corresponding dependency instructions and avoid mixing incompatible system and source installations.

## Running the Camera Node

Run the standalone camera node:

```bash
ros2 run benzene_camera camera_node
```

Launch the composable node using the provided launch file:

```bash
ros2 launch benzene_camera camera.launch.py
```

The launch command requires the corresponding launch file to be included and installed by the package.

## ROS 2 Interfaces

### Topics

| Topic | Message type | Description |
|---|---|---|
| `~/image_raw` | `sensor_msgs/msg/Image` | Raw camera images |
| `~/image_raw/compressed` | `sensor_msgs/msg/CompressedImage` | Compressed camera images |
| `~/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera calibration and intrinsic parameters |

The `~` prefix denotes a node-private topic. The fully resolved topic name depends on the node name and namespace.

### Services

| Service | Type | Description |
|---|---|---|
| `~/set_camera_info` | `sensor_msgs/srv/SetCameraInfo` | Update camera calibration information |

## Camera Configuration

The camera stream is configured when the node starts.

| Parameter | Description |
|---|---|
| `camera` | Camera index or camera name |
| `role` | Stream role, such as `raw`, `still`, `video`, or `viewfinder` |
| `format` | Requested pixel format |
| `width` | Desired image width |
| `height` | Desired image height |
| `sensor_mode` | Desired raw sensor resolution in `width:height` format |
| `orientation` | Camera orientation: 0, 90, 180, or 270 degrees |
| `camera_info_url` | URL of the camera calibration file |
| `frame_id` | Frame identifier in the image message header |
| `use_node_time` | Whether to use node time instead of the sensor timestamp |

Available formats and supported resolutions depend on the camera hardware and libcamera implementation.

### Setting Parameters

Parameters can be passed when starting the node. For example:

```bash
ros2 run benzene_camera camera_node --ros-args \
  -p width:=640 \
  -p height:=480
```

For a fixed frame duration of 50,000 microseconds, equivalent to 20 Hz, if the camera exposes `FrameDurationLimits`:

```bash
ros2 run benzene_camera camera_node --ros-args \
  -p 'FrameDurationLimits:=[50000,50000]'
```

Check the actual supported parameters for your installed version before using camera-specific controls.

## Camera Calibration

The node uses a camera information manager to load and publish calibration parameters, including camera intrinsics and distortion coefficients.

The `camera_info_url` parameter specifies the calibration file. Its default location is typically:

```text
~/.ros/camera_info/$NAME.yaml
```

When providing a custom calibration file, use a file URL, for example:

```text
file:///home/user/camera/calibration.yaml
```

A calibration file can be generated using the ROS 2 `camera_calibration` package. Without calibration data, the node may publish zero-initialized camera parameters.

## Troubleshooting

| Problem | Suggested action |
|---|---|
| No camera detected | Check the camera connection and whether libcamera recognizes the device |
| Camera node fails to start | Check the installed dependencies and terminal logs |
| Requested resolution is unavailable | Use a resolution and pixel format supported by the camera |
| Image buffers cannot be allocated | Reduce resolution or select a lower-memory pixel format |
| Calibration