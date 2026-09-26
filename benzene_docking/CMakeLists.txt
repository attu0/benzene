cmake_minimum_required(VERSION 3.8)

project(benzene_docking)

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
find_package(ament_cmake_python REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(apriltag_ros REQUIRED)
find_package(apriltag_msgs REQUIRED)
find_package(image_proc REQUIRED)
find_package(tf2_ros REQUIRED)

# =============================================================================
# Dock Pose Publisher
# =============================================================================

add_executable(
  detected_dock_pose_publisher
  src/detected_dock_pose_publisher.cpp
)

ament_target_dependencies(
  detected_dock_pose_publisher
  rclcpp
  geometry_msgs
  tf2_ros
)

install(
  TARGETS
    detected_dock_pose_publisher
  DESTINATION
    lib/${PROJECT_NAME}
)

# =============================================================================
# Install
# =============================================================================

install(
  DIRECTORY
    launch
    config
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