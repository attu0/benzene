cmake_minimum_required(VERSION 3.8)

project(benzene_gazebo)

# =============================================================================
# Compiler Options
# =============================================================================

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
  )
endif()

# =============================================================================
# Dependencies
# =============================================================================

find_package(ament_cmake REQUIRED)

# Suppress the deprecation message emitted by the legacy tl_expected package.
set(tl_expected_DEPRECATED_QUIET TRUE)

find_package(controller_manager REQUIRED)
find_package(gz_ros2_control REQUIRED)
find_package(rclcpp REQUIRED)
find_package(ros_gz REQUIRED)
find_package(ros_gz_bridge REQUIRED)
find_package(ros_gz_image REQUIRED)
find_package(ros_gz_sim REQUIRED)
find_package(ros2_control REQUIRED)
find_package(ros2_controllers REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(xacro REQUIRED)

# =============================================================================
# Install
# =============================================================================

install(
  DIRECTORY
    launch
    models
    worlds
    config
    rviz
  DESTINATION
    share/${PROJECT_NAME}
)

# =============================================================================
# Testing
# =============================================================================

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  # Disable checks that are not applicable to this package.
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)

  ament_lint_auto_find_test_dependencies()
endif()

# =============================================================================
# Package
# =============================================================================

ament_package()