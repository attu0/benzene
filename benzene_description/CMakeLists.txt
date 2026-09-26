cmake_minimum_required(VERSION 3.8)

project(benzene_description)

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
find_package(urdf_tutorial REQUIRED)

# =============================================================================
# Install
# =============================================================================

install(
  DIRECTORY
    config
    launch
    meshes
    rviz
    urdf
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