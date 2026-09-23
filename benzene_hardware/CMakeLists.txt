cmake_minimum_required(VERSION 3.16)
project(benzene_hardware LANGUAGES CXX)

if(CMAKE_CXX_COMPILER_ID MATCHES "(GNU|Clang)")
  add_compile_options(-Wall -Wextra)
endif()

set(THIS_PACKAGE_INCLUDE_DEPENDS
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)

find_package(ament_cmake REQUIRED)
foreach(Dependency IN ITEMS ${THIS_PACKAGE_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()

add_library(
  benzene_hardware
  SHARED
  hardware/diffbot_system.cpp
)
target_compile_features(benzene_hardware PUBLIC cxx_std_17)
target_include_directories(benzene_hardware PUBLIC
$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/hardware/include>
$<INSTALL_INTERFACE:include/benzene_hardware>
)
ament_target_dependencies(
  benzene_hardware PUBLIC
  ${THIS_PACKAGE_INCLUDE_DEPENDS}
)

target_link_libraries(benzene_hardware PUBLIC serial)

target_compile_definitions(${PROJECT_NAME} PRIVATE "DIFFDRIVE_ARDUINO_BUILDING_DLL")

pluginlib_export_plugin_description_file(hardware_interface diffdrive_arduino.xml)

install(
  DIRECTORY hardware/include/
  DESTINATION include/benzene_hardware
)
install(
  DIRECTORY description/launch description/ros2_control description/urdf description/rviz
  DESTINATION share/benzene_hardware
)
install(
  DIRECTORY bringup/launch bringup/config
  DESTINATION share/benzene_hardware
)
install(TARGETS benzene_hardware
  EXPORT export_benzene_hardware
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
endif()

ament_export_targets(export_benzene_hardware HAS_LIBRARY_TARGET)
ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})
ament_package()
