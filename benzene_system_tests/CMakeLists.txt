cmake_minimum_required(VERSION 3.8)

project(benzene_system_tests)

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
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rcl_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(benzene_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)

# =============================================================================
# System Test Nodes
# =============================================================================

add_executable(
  square_movemet_test
  src/square_movemet_test.cpp
)

add_executable(
  mecanum_parameters_node
  src/mecanum_parameters_node.cpp
)

add_executable(
  timed_rotation_action_server
  src/timed_rotation_action_server.cpp
)

add_executable(
  timed_rotation_action_client
  src/timed_rotation_action_client.cpp
)

add_executable(
  set_cleaning_state_service
  src/set_cleaning_state_service.cpp
)

# =============================================================================
# Target Dependencies
# =============================================================================

ament_target_dependencies(
  square_movemet_test
  rclcpp
  geometry_msgs
  std_msgs
  nav_msgs
  tf2
)

ament_target_dependencies(
  mecanum_parameters_node
  rclcpp
  geometry_msgs
  std_msgs
  rcl_interfaces
)

ament_target_dependencies(
  timed_rotation_action_server
  rclcpp
  rclcpp_action
  geometry_msgs
  benzene_msgs
)

ament_target_dependencies(
  timed_rotation_action_client
  rclcpp
  rclcpp_action
  benzene_msgs
  std_msgs
)

ament_target_dependencies(
  set_cleaning_state_service
  rclcpp
  benzene_msgs
)

# =============================================================================
# Install
# =============================================================================

install(
  TARGETS
    square_movemet_test
    mecanum_parameters_node
    timed_rotation_action_server
    timed_rotation_action_client
    set_cleaning_state_service
  DESTINATION
    lib/${PROJECT_NAME}
)

install(
  PROGRAMS
    src/square_controller.py
  DESTINATION
    lib/${PROJECT_NAME}
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