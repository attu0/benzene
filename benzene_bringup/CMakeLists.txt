cmake_minimum_required(VERSION 3.8)

project(benzene_bringup)

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
find_package(geometry_msgs REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets)

# =============================================================================
# Keyboard Teleoperation
# =============================================================================

add_executable(
  teleop_keyboard
  src/teleop_keyboard.cpp
)

ament_target_dependencies(
  teleop_keyboard
  rclcpp
  geometry_msgs
)

target_link_libraries(
  teleop_keyboard
  Qt5::Widgets
)

install(
  TARGETS
    teleop_keyboard
  DESTINATION
    lib/${PROJECT_NAME}
)

# =============================================================================
# Install
# =============================================================================

install(
  DIRECTORY
    launch
    scripts
  DESTINATION
    share/${PROJECT_NAME}/
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