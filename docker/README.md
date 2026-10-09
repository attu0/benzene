# Benzene Docker

Docker setup for running the Benzene robot workspace (ROS 2 Jazzy, Gazebo Harmonic, Nav2, RViz2) on a Linux host.

## Contents

| File | Purpose |
|---|---|
| `Dockerfile` | Builds the image: ROS 2 Jazzy base, Gazebo, Nav2, ros2_control, robot_localization, then builds the workspace |
| `build.sh` | Builds the `benzene:latest` image and creates the shared folder on the host |
| `docker-compose.yml` | Runs the container with GUI, device and shared-folder access |
| `workspace.sh` | Runs during the image build: `rosdep install` and `colcon build --symlink-install` |
| `entrypoint.sh` | Runs on every container start: sets `ROS_DOMAIN_ID`, sources ROS and the workspace |
| `bash_aliases.txt` | Aliases appended to the container's `.bashrc` |

## Requirements

- Linux host with a display server (X11)
- Docker Engine with the Compose plugin
- Roughly 20 GB of free disk space (the image is about 8 GB on disk, and the build needs extra for layers)

## Build

```bash
cd ~/ros2_ws/src/benzene/docker
./build.sh
```

The first build takes a while (about 15 to 25 minutes) because of the apt and ROS package installs. Later builds reuse cached layers.

For a completely fresh build with no cache:

```bash
./build.sh --no-cache
```

## Run

```bash
cd ~/ros2_ws/src/benzene/docker
xhost +local:docker
docker compose up -d
docker exec -it benzene bash
```

- `xhost +local:docker` allows GUI apps (RViz, Gazebo) in the container to open windows on your display. Run it once per login session.
- `docker compose up -d` starts the container in the background.
- `docker exec -it benzene bash` opens a shell inside it. Open more terminals with the same command.

## Aliases inside the container

| Alias | What it does |
|---|---|
| `x3 [cafe\|office]` | Launches the Gazebo simulation (default world: warehouse) |
| `x3_nav [slam] [cafe\|office]` | Launches Gazebo with Nav2 (default world: warehouse). Add `slam` first to run SLAM instead of using a saved map |
| `build_ros2_ws` | Rebuilds the workspace (`colcon build --symlink-install`) and sources it |

Examples:

```bash
x3                 # warehouse world
x3 cafe            # cafe world
x3_nav office      # Nav2 with the office map
x3_nav slam cafe   # SLAM in the cafe world
```

## Stop and clean up

```bash
docker compose down                  # stop and remove the container
docker compose up -d --force-recreate   # recreate it (resets any edits made inside the container)
```

## Notes

- **Paths:** inside the container your home is `/root`, so the workspace is at `/root/ros2_ws`. The launch scripts use `$HOME` so they work both on the host and in the container.
- **Source code is copied into the image at build time.** Edits on the host do not appear in the container until you rebuild with `./build.sh`, or mount the source by adding this under `volumes` in `docker-compose.yml`:

  ```yaml
  - ${HOME}/ros2_ws/src/benzene:/root/ros2_ws/src/benzene
  ```

  Then recreate the container and run `build_ros2_ws` after changing packages.
- **Shared folder:** `~/atharv/shared/ros2` on the host is mounted at `/root/shared/ros2` in the container. It stores `ros_domain_id.txt` (default `0`), which sets `ROS_DOMAIN_ID`. Computers that should talk to each other need the same value.
- **Hardware access:** the container runs with `privileged: true`, `network_mode: host` and `/dev` mounted, so USB and serial devices (Arduino) and `/dev/i2c-*` (IMU) are visible if connected to the host.
- **Build context size:** `.dockerignore` in the repo root excludes `.git`, `build/`, `install/`, `log/`, virtualenvs, and rosbags. If the build context grows to several GB, check what is being copied.

## Troubleshooting

| Problem | Fix |
|---|---|
| `no space left on device` during build | Free disk space: `docker builder prune -f` and `docker image prune -f`. Check that `.dockerignore` excludes `.venv` and `build/`. |
| `Cannot locate rosdep definition for [...]` | A `package.xml` lists a dependency that is not a valid rosdep key. Fix or remove it. For `ament_python`, use `<build_type>` in `<export>` instead of a dependency. |
| GUI windows do not open | Run `xhost +local:docker` on the host and check that `echo $DISPLAY` is set. |
| Map or world not found | The container has an old copy of the scripts. Rebuild with `./build.sh` or mount the source folder. |
| Gazebo cannot find models | Check that `GZ_SIM_RESOURCE_PATH` in the launch scripts includes `benzene_gazebo/models`. |
| Edits to scripts disappear | The container was recreated. Make the edit on the host, then rebuild or mount the source. |