this is readme to guide for the docker

to build

cd ~/ros2_ws/src/benzene/docker
./build.sh

to execute

cd ~/ros2_ws/src/benzene/docker
xhost +local:docker
docker compose up -d
docker exec -it benzene bash
