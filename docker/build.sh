#!/bin/bash

# Get the absolute path of the directory containing this script (docker directory)
SCRIPT_PATH=$(dirname $(realpath "$0"))

# Get the parent directory path (benzene repo root)
PARENT_PATH=$(dirname "$SCRIPT_PATH")

build_docker_image()
{
    LOG="Building Docker image benzene:latest ..."
    print_debug

    # Pass --no-cache as an argument when you want a fully fresh build:
    #   ./build.sh --no-cache
    sudo docker image build -f $SCRIPT_PATH/Dockerfile -t benzene:latest $PARENT_PATH "$@"
}

create_shared_folder()
{
    if [ ! -d "$HOME/atharv/shared/ros2" ]; then
        LOG="Creating $HOME/atharv/shared/ros2 ..."
        print_debug
        mkdir -p $HOME/atharv/shared/ros2
    fi
}

print_debug()
{
    echo ""
    echo $LOG
    echo ""
}

create_shared_folder
build_docker_image "$@"