# Benzene DAgger

## Overview

The `benzene_dagger` package trains the Benzene robot to follow a yellow centerline from camera images using **behavioral cloning** and **DAgger** (Dataset Aggregation).

- A classical OpenCV + PD **expert** produces the correct steering for every camera frame.
- A CNN **learner** is trained to imitate the expert from images alone.
- A **mixer** node decides, with probability `beta`, whether the expert or the learner drives the robot. The expert keeps labeling every frame, even while the learner drives, so the dataset covers the states the learner actually visits (including its mistakes).

## Features

- Simulates the robot in Gazebo and visualizes it in RViz, with LiDAR rays from `scan_marker`.
- Yellow-line detection with lateral and heading error.
- PD expert that publishes labels only (never drives directly).
- DAgger mixer that is the only node publishing to the drive topic.
- Synchronized (image, expert action) dataset collection.
- Training on all episodes with a time-based validation split and flip augmentation.
- CNN controller that runs the learned policy.

## Architecture

```
/cam_1/color/image_raw
        |
        +--> line_detector --> /line/lateral_error, /line/heading_error
        |                               |
        |                               v
        |                        expert_controller --> /expert/cmd_vel (TwistStamped) --+
        |                                                                               |
        +--> cnn_controller ----------------------> /learner/cmd_vel (TwistStamped) ----+
        |                                                                               v
        |                                                                         dagger_mixer
        |                                                                               |
        |                                                                               v
        |                                              /diff_drive_controller/cmd_vel (TwistStamped)
        |
        +--> data_collector  (saves image + /expert/cmd_vel label)
```

| Topic | Type | Publisher |
|---|---|---|
| `/line/lateral_error`, `/line/heading_error` | `std_msgs/Float32` | `line_detector` |
| `/expert/cmd_vel` | `geometry_msgs/TwistStamped` | `expert_controller` |
| `/learner/cmd_vel` | `geometry_msgs/TwistStamped` | `cnn_controller` |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/TwistStamped` | `dagger_mixer` (only) |
| `/dagger/active_source` | `std_msgs/String` | `dagger_mixer` (`expert` or `learner`) |

## Requirements

- ROS 2 Jazzy
- Gazebo and RViz
- `benzene_bringup`, `benzene_gazebo`, `benzene_description`
- Python 3 with `torch`, `numpy`, `opencv-python`, `cv_bridge`, `message_filters`
- A display (the line detector opens OpenCV windows)
- The Benzene workspace built successfully

**Python environment:** ROS nodes and the training script must be run with a Python that can import both `rclpy` and `torch`. If you use a virtual environment, create it with system packages:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install torch
python3 -c "import torch, rclpy; print('ok')"
```

## Build

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select benzene_dagger --symlink-install
source install/setup.bash
ros2 pkg executables benzene_dagger
```

The last command should list: `cnn_controller.py`, `dagger_mixer.py`, `data_collector.py`, `expert_controller.py`, `line_detector.py`, `scan_marker`, `train_behavioral_cloning.py`.

Rebuild after adding new scripts or changing `CMakeLists.txt`. With `--symlink-install`, edits to existing files take effect without rebuilding.

## 1. Run the Simulation Only

```bash
ros2 launch benzene_dagger dagger_sim.launch.py
```

This launches Gazebo (`race2.sdf`), RViz and the scan marker. Nothing drives the robot in this mode.

**Manual driving:** run `teleop_keyboard` only with this launch file:

```bash
ros2 run benzene_bringup teleop_keyboard
```

Do **not** run `teleop_keyboard` while `data_collection.launch.py` is running. The mixer publishes the drive command continuously, so manual commands would conflict with it.

## 2. Collect Expert Data (Iteration 0)

```bash
ros2 launch benzene_dagger data_collection.launch.py
```

**Important:** this launch file includes the simulation. Do not launch `dagger_sim.launch.py` separately.

With the default `beta:=1.0` the expert drives, and the robot follows the yellow line on its own. Each run writes a new folder:

```
benzene_dagger/dataset/episode_YYYYMMDD_HHMMSS/
    images/000000.jpg ...
    labels.csv        # frame, image_file, stamp_sec, linear_x, angular_z
```

Stop with Ctrl+C when finished. Aim for several laps (a few thousand frames).

### Launch arguments

| Argument | Default | Meaning |
|---|---|---|
| `beta` | `1.0` | Probability that the expert drives (1.0 = pure expert, 0.0 = pure learner) |
| `mix_hold_time` | `1.0` | Seconds between re-sampling expert/learner |
| `use_learner` | `false` | Start the CNN learner (requires a trained model) |

### Check the data

```bash
D=~/ros2_ws/src/benzene/benzene_dagger/dataset
EP=$(ls -d $D/episode_* | tail -1)
echo "rows: $(($(wc -l < $EP/labels.csv) - 1))   images: $(ls $EP/images | wc -l)"
```

Rows and images should match. Check that the `angular_z` values are not almost all zero, and that the lap includes both left and right turns. A one-directional lap produces a one-sided model, so driving a lap in the reverse direction helps.

## 3. Train the Model

```bash
cd ~/ros2_ws
python3 src/benzene/benzene_dagger/scripts/train_behavioral_cloning.py
```

By default, the script trains on **every** episode folder under `dataset/` that has `labels.csv` and `images/`. Folders without them are skipped. To pick specific episodes:

```bash
python3 src/benzene/benzene_dagger/scripts/train_behavioral_cloning.py \
    --episodes episode_20260926_163735 test1 --epochs 40
```

What the script does:

- Holds out the **last 20% of each episode** for validation, so neighboring frames never leak across the split.
- Augments training frames with a random horizontal flip (and negates `angular_z`) plus a small brightness change.
- Crops the top 35% of the image (matching the line detector's region of interest), then resizes to 200x120.
- Prints baseline validation errors (predict 0, predict the train mean). The model must beat both clearly.
- Saves the best model, with its `crop_top` and `image_size`, to `benzene_dagger/models/benzene_bc_model.pth`.

Validation loss measures how closely the model copies the expert on recorded frames. It does not guarantee that the robot stays on the line when it drives, so test in closed loop (next section).

## 4. Run the Learned Policy

```bash
ros2 launch benzene_dagger data_collection.launch.py use_learner:=true beta:=0.0
```

The learner drives and the expert still labels every frame. Look for these log lines:

- `Loaded model: ...benzene_bc_model.pth`
- `CNN command: linear=0.200, angular=...`

```bash
ros2 topic echo /dagger/active_source --once   # data: learner
```

If the robot leaves the line and stops, the mixer logs a warning when the chosen source goes stale. Stop and restart the run rather than recording a long stretch off the line.

## 5. The DAgger Loop

1. **Iteration 0:** collect expert data with `beta:=1.0` (section 2) and train (section 3).
2. **Iteration 1:** collect with the learner mostly driving:
   ```bash
   ros2 launch benzene_dagger data_collection.launch.py use_learner:=true beta:=0.3
   ```
3. Retrain. The new episode folder is aggregated automatically.
4. Repeat with a lower `beta` (0.3, then 0.1, then 0.0) as the policy improves.

You can change `beta` while a run is in progress:

```bash
ros2 param set /dagger_mixer beta 0.5
```

## Mixer Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `beta` | `1.0` | Probability that the expert drives |
| `mix_hold_time` | `1.0` | Seconds between re-sampling the source |
| `rate` | `20.0` | Publish rate to the drive topic (Hz) |
| `source_timeout` | `0.5` | A source older than this is stale, and the robot stops |
| `expert_topic` | `/expert/cmd_vel` | Expert input |
| `learner_topic` | `/learner/cmd_vel` | Learner input |
| `drive_topic` | `/diff_drive_controller/cmd_vel` | Output to the robot |

## Verification Checklist

With `data_collection.launch.py` running:

```bash
ros2 node list | grep -E "mixer|collector|expert|yellow"
ros2 topic info /diff_drive_controller/cmd_vel -v     # Publisher count: 1 (dagger_mixer); type TwistStamped
ros2 topic echo /expert/cmd_vel --once                # linear.x ~ 0.2
ros2 topic echo /dagger/active_source --once          # expert (or learner)
ros2 topic echo /diff_drive_controller/cmd_vel --once
```

The launch log should show `Mixer started: ... beta=...` and `Recording to .../dataset/episode_...`.

## Package Layout

```
benzene_dagger/
    CMakeLists.txt
    package.xml
    launch/
        dagger_sim.launch.py          # Gazebo + RViz + scan_marker
        data_collection.launch.py     # full pipeline (expert, mixer, collector, optional learner)
    rviz/dagger.rviz
    scripts/
        line_detector.py
        expert_controller.py
        dagger_mixer.py
        cnn_controller.py
        data_collector.py
        train_behavioral_cloning.py
    src/scan_marker.cpp
    dataset/                          # episode_* folders (generated)
    models/                           # benzene_bc_model.pth (generated)
```

## Troubleshooting

- **Package or executable not found:** build, then `source install/setup.bash`. Check with `ros2 pkg executables benzene_dagger`.
- **A new script is not found:** it must be listed in `install(PROGRAMS ...)` in `CMakeLists.txt`. Rebuild after adding it.
- **`/dagger_mixer` or another node is missing from `ros2 node list`:** the launch file may be an old copy. Check `grep -c mixer src/benzene/benzene_dagger/launch/data_collection.launch.py`, which should be above 0.
- **A node starts and exits immediately with no output:** the script may contain the wrong code. Check the first lines of the file (`head -5`) and make sure it ends with `if __name__ == '__main__': main()`.
- **Drive topic has more than one publisher or the robot jerks:** something else is publishing to `/diff_drive_controller/cmd_vel` (for example `teleop_keyboard`). Stop it, because only `dagger_mixer` should publish there.
- **Robot does not move:**
  - The detector window shows `LINE NOT DETECTED`. The expert then publishes nothing, and the mixer logs `"expert" command is stale`.
  - Check `ros2 topic hz /line/lateral_error`.
  - Check that the robot spawns on the line in `race2.sdf`.
- **No labels when the line is lost:** by design, the expert publishes nothing when it cannot see the line, so recovery frames from fully off-line states are not recorded. Keep runs on or near the line.
- **`ModuleNotFoundError: torch` or `rclpy`:** see the Python environment note under Requirements.
- **`Model not found`:** train first (section 3). The model is expected at `benzene_dagger/models/benzene_bc_model.pth`.
- **Robot behaves badly after retraining:** `train_behavioral_cloning.py` and `cnn_controller.py` must be the matching versions (both apply the top crop). Old checkpoints without `crop_top` are run without a crop.
- **Expert rate is below 20 Hz:** the controller's timer follows simulation time, so a real-time factor below 1 lowers the rate.
- **`cv2.imshow` errors over SSH:** the line detector needs a display.

## Known Limitations

- The learner predicts only `angular_z`. Linear speed is fixed at 0.20 m/s.
- The expert gives no label when the line is lost.
- The first model is trained on a small dataset, so expect overfitting until more DAgger iterations are collected.
- Lap data is naturally biased toward the track's dominant turn direction. Flip augmentation corrects the label balance, and reverse-direction laps help further.

## Related Packages

- `benzene_bringup`: robot bringup and keyboard teleoperation.
- `benzene_gazebo`: simulation assets and worlds.
- `benzene_description`: robot model.
- `benzene_control`: robot control functionality.