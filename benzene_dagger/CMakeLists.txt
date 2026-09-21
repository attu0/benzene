cmake_minimum_required(VERSION 3.8)

project(benzene_dagger)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

add_executable(teleop_keyboard
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
  DESTINATION lib/${PROJECT_NAME}
)

add_executable(scan_marker src/scan_marker.cpp)

ament_target_dependencies(
  scan_marker
  rclcpp
  sensor_msgs
  visualization_msgs
  geometry_msgs
)

install(
  TARGETS scan_marker
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY
    launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()