cmake_minimum_required(VERSION 3.5)

project(benzene_explore)

# =============================================================================
# C/C++ Standards
# =============================================================================

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

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
# ROS 2 Distribution Compatibility
# =============================================================================

if(NOT DEFINED ENV{ROS_DISTRO})
  message(FATAL_ERROR "ROS_DISTRO is not defined.")
endif()

if("$ENV{ROS_DISTRO}" STREQUAL "eloquent")
  message(STATUS "Build for ROS 2 Eloquent")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DELOQUENT")
elseif("$ENV{ROS_DISTRO}" STREQUAL "dashing")
  message(STATUS "Build for ROS 2 Dashing")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DDASHING")
else()
  message(STATUS "Build for ROS 2: $ENV{ROS_DISTRO}")
endif()

# =============================================================================
# Dependencies
# =============================================================================

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(map_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(benzene_explore_msgs REQUIRED)

# =============================================================================
# Dependencies List
# =============================================================================

set(DEPENDENCIES
  rclcpp
  std_msgs
  sensor_msgs
  tf2
  tf2_ros
  nav2_msgs
  nav_msgs
  map_msgs
  nav2_costmap_2d
  visualization_msgs
)

# =============================================================================
# Include Directories
# =============================================================================

include_directories(
  include
)

# =============================================================================
# Install Headers
# =============================================================================

install(
  DIRECTORY
    include/benzene_explore/
  DESTINATION
    include/benzene_explore/
)

# =============================================================================
# Install Configuration
# =============================================================================

install(
  DIRECTORY
    config
  DESTINATION
    share/${PROJECT_NAME}
)

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}
)

# =============================================================================
# Explore Node
# =============================================================================

add_executable(
  explore
  src/costmap_client.cpp
  src/explore.cpp
  src/frontier_search.cpp
)

target_include_directories(
  explore
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/benzene_explore>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(
  explore
  PUBLIC
    ${benzene_explore_msgs_TARGETS}
    ${geometry_msgs_TARGETS}
    ${map_msgs_TARGETS}
    ${nav2_msgs_TARGETS}
    ${nav_msgs_TARGETS}
    ${std_msgs_TARGETS}
    ${visualization_msgs_TARGETS}
    nav2_costmap_2d::filters
    rclcpp::rclcpp
    tf2::tf2
    tf2_ros::tf2_ros
)

if(nav2_msgs_VERSION VERSION_GREATER_EQUAL "1.3.0")
  target_compile_definitions(
    explore
    PRIVATE
      NAV2_RESULT_HAS_ERROR_CODE
  )
endif()

install(
  TARGETS
    explore
  DESTINATION
    lib/${PROJECT_NAME}
)

# =============================================================================
# Gazebo Flags
# =============================================================================

set(
  CMAKE_CXX_FLAGS
  "${CMAKE_CXX_FLAGS} ${GAZEBO_CXX_FLAGS}"
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

  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(
    test_explore
    test/test_explore.cpp
  )

  target_link_libraries(
    test_explore
    ${geometry_msgs_TARGETS}
  )
endif()

# =============================================================================
# Export Dependencies
# =============================================================================

ament_export_dependencies(
  benzene_explore_msgs
  geometry_msgs
  map_msgs
  nav2_costmap_2d
  nav2_msgs
  nav_msgs
  rclcpp
  std_msgs
  tf2
  tf2_ros
  visualization_msgs
)

ament_export_include_directories(
  include/benzene_explore
)

# =============================================================================
# Package
# =============================================================================

ament_package()