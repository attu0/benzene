Build
bash
cd ~/ros2_ws
colcon build --packages-select benzene_dagger --symlink-install
source install/setup.bash

1. Check the simulation and teleop
bash
ros2 launch benzene_dagger dagger_sim.launch.py      # Gazebo + RViz + scan_marker
ros2 run benzene_bringup teleop_keyboard

2. Collect expert data

Don’t also run the sim launch, because this one includes it.

bash
ros2 launch benzene_dagger data_collection.launch.py


3. Train

Edit DATASET_DIR in train_behavioral_cloning.py to your new episode folder. It’s currently hard-coded to episode_20260926_163735. Then:

bash
python3 ~/ros2_ws/src/benzene/benzene_dagger/scripts/train_behavioral_cloning.py


4. Run the learned policy
bash
ros2 launch benzene_dagger dagger_sim.launch.py
# second terminal:
python3 ~/ros2_ws/src/benzene/benzene_dagger/scripts/cnn_controller.py --ros-args -p use_sim_time:=true