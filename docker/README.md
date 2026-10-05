# Benzene Diff-Drive Robot Workspace Setup

This repository provides a containerized Docker environment for the Benzene Diff-Drive Robot. The setup automates the installation of ROS 2 Jazzy, configures system dependencies for 3D simulation (Gazebo), and establishes a ready-to-use development workspace with graphical tool support (RViz2, Gazebo).

## Prerequisites

Before getting started, ensure you have the following installed on your host machine:
* **Docker Engine**
* **Docker Compose**
* **X11 Server** (for Linux hosts, this is typically built-in. If on Windows/Mac, you will need tools like VcXsrv or XQuartz).

---

## 🚀 Quick Start Guide

Follow these commands to build the environment, enable graphical interfaces, and start developing.

### 1. Enable GUI Access (X11 Forwarding)
To allow the Docker container to display graphical applications (like Gazebo and RViz) on your host machine's monitor, you need to grant local access to the X server:
```bash
xhost +local:root
```
*(Note: You may need to run this command every time you restart your host computer).*

### 2. Build the Docker Image
Navigate to the directory containing `build.sh` and run it. This script automatically creates a shared host directory at `$HOME/atharv/shared/ros2` and builds the `benzene:latest` Docker image:
```bash
./build.sh
```

### 3. Start the Container
Once the build is complete, launch the container in the background using Docker Compose:
```bash
docker compose up -d
```
The container runs indefinitely in the background.

### 4. Access the Container
To open an interactive terminal session inside the running container, execute:
```bash
docker exec -it benzene bash
```
You can open multiple terminals by running this command in new terminal tabs.

### 5. Stop the Container
When you are done working, you can stop and remove the running container with:
```bash
docker compose down
```

---

## 🛠️ Built-in Shortcuts (Aliases)

Once inside the container, several bash aliases are available to speed up your workflow (defined in `bash_aliases.txt`):

* **Launch Simulation:**
  ```bash
  x3
  ```
  *(Runs the Gazebo simulation script)*
* **Launch Navigation:**
  ```bash
  x3_nav
  ```
  *(Runs the navigation stack script)*
* **Rebuild Workspace:**
  ```bash
  build_ros2_ws
  ```
  *(Navigates to `~/ros2_ws`, runs `colcon build --symlink-install`, and sources the setup script)*

---

## 📂 System Components

The environment is constructed using the following configuration files:

* **`build.sh`**: Automates directory creation and builds the Docker image without using the cache.
* **`Dockerfile`**: Establishes the environment using `ros:jazzy-ros-base`. Installs Gazebo, Navigation2, EKF sensor fusion, and configures Mesa graphics drivers for 3D rendering.
* **`docker-compose.yml`**: Defines container execution with host networking, privileged access, and mounts X11 sockets/`.Xauthority` to enable graphical interfaces.
* **`workspace.sh`**: Initializes the ROS 2 workspace at `/root/ros2_ws`, resolves dependencies using `rosdep install`, and compiles the workspace using `colcon`.
* **`entrypoint.sh`**: Sets up the `XDG_RUNTIME_DIR` for Linux desktop apps, manages the `ROS_DOMAIN_ID`, and sources the necessary setup files upon container boot.

---

## 🌐 Multi-Robot Networking

The environment supports multi-robot communication through a `ros_domain_id.txt` file located in the shared volume (`$HOME/atharv/shared/ros2`).

* If this file does not exist upon container startup, `entrypoint.sh` creates it with a default value of `0`.
* This value is exported as the `ROS_DOMAIN_ID` within the container.
* To change the domain ID (e.g., to isolate your robot's network from others), simply edit `ros_domain_id.txt` on your host machine and restart your container's terminal sessions.