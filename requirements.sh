#!/usr/bin/env bash
#
# benzene_robot -- task dependency installer
#
# Usage:
#   ./requirements.sh            install what is missing
#   ./requirements.sh --check    report what is missing, install nothing

set -euo pipefail

ROS_DISTRO_REQUIRED="jazzy"
UBUNTU_VERSION_REQUIRED="24.04"

ROS_PACKAGES_EXPECTED=(
  # Core ROS 2 packages, Lifecycles, & Messaging
  ros-${ROS_DISTRO_REQUIRED}-rclcpp
  ros-${ROS_DISTRO_REQUIRED}-rclcpp-action
  ros-${ROS_DISTRO_REQUIRED}-rclcpp-lifecycle
  ros-${ROS_DISTRO_REQUIRED}-rclpy
  ros-${ROS_DISTRO_REQUIRED}-rcl-interfaces
  ros-${ROS_DISTRO_REQUIRED}-builtin-interfaces
  ros-${ROS_DISTRO_REQUIRED}-std-msgs
  ros-${ROS_DISTRO_REQUIRED}-geometry-msgs
  ros-${ROS_DISTRO_REQUIRED}-sensor-msgs
  ros-${ROS_DISTRO_REQUIRED}-trajectory-msgs
  ros-${ROS_DISTRO_REQUIRED}-nav-msgs
  ros-${ROS_DISTRO_REQUIRED}-map-msgs
  ros-${ROS_DISTRO_REQUIRED}-visualization-msgs

  # Control, Hardware Interfaces, & Simulation
  ros-${ROS_DISTRO_REQUIRED}-controller-manager
  ros-${ROS_DISTRO_REQUIRED}-ros2-control
  ros-${ROS_DISTRO_REQUIRED}-ros2-controllers
  ros-${ROS_DISTRO_REQUIRED}-gz-ros2-control
  ros-${ROS_DISTRO_REQUIRED}-ros-gz
  ros-${ROS_DISTRO_REQUIRED}-ros-gz-bridge
  ros-${ROS_DISTRO_REQUIRED}-ros-gz-image
  ros-${ROS_DISTRO_REQUIRED}-ros-gz-sim
  ros-${ROS_DISTRO_REQUIRED}-hardware-interface
  ros-${ROS_DISTRO_REQUIRED}-pluginlib
  ros-${ROS_DISTRO_REQUIRED}-joint-state-broadcaster
  ros-${ROS_DISTRO_REQUIRED}-diff-drive-controller
  ros-${ROS_DISTRO_REQUIRED}-ros2controlcli
  ros-${ROS_DISTRO_REQUIRED}-ros2-controllers-test-nodes

  # Navigation, Localization, Transforms, and Vision
  ros-${ROS_DISTRO_REQUIRED}-tf2
  ros-${ROS_DISTRO_REQUIRED}-tf2-ros
  ros-${ROS_DISTRO_REQUIRED}-tf-transformations
  ros-${ROS_DISTRO_REQUIRED}-navigation2
  ros-${ROS_DISTRO_REQUIRED}-nav2-bringup
  ros-${ROS_DISTRO_REQUIRED}-nav2-common
  ros-${ROS_DISTRO_REQUIRED}-nav2-costmap-2d
  ros-${ROS_DISTRO_REQUIRED}-nav2-msgs
  ros-${ROS_DISTRO_REQUIRED}-nav2-simple-commander
  ros-${ROS_DISTRO_REQUIRED}-slam-toolbox
  ros-${ROS_DISTRO_REQUIRED}-robot-localization
  ros-${ROS_DISTRO_REQUIRED}-cv-bridge
  ros-${ROS_DISTRO_REQUIRED}-image-proc
  ros-${ROS_DISTRO_REQUIRED}-image-view
  ros-${ROS_DISTRO_REQUIRED}-message-filters
  ros-${ROS_DISTRO_REQUIRED}-apriltag-ros
  ros-${ROS_DISTRO_REQUIRED}-apriltag-msgs

  # Hardware & Bringup
  ros-${ROS_DISTRO_REQUIRED}-xacro
  ros-${ROS_DISTRO_REQUIRED}-urdf-tutorial
  ros-${ROS_DISTRO_REQUIRED}-rplidar-ros
  ros-${ROS_DISTRO_REQUIRED}-v4l2-camera
  ros-${ROS_DISTRO_REQUIRED}-robot-state-publisher

  # Tools & Visualization
  ros-${ROS_DISTRO_REQUIRED}-rqt-robot-steering
  ros-${ROS_DISTRO_REQUIRED}-rviz-imu-plugin
  ros-${ROS_DISTRO_REQUIRED}-rviz2
)

SYSTEM_PACKAGES=(
  # Python dependencies & I2C/SMBus
  python3-numpy
  python3-opencv
  python3-pip
  python3-smbus2

  # C++ Hardware & Serial drivers
  libserial-dev
  libboost-dev
)

BUILD_PACKAGES=(
  build-essential
  python3-colcon-common-extensions
  python3-rosdep
  ros-${ROS_DISTRO_REQUIRED}-ament-cmake
  ros-${ROS_DISTRO_REQUIRED}-ament-cmake-python
  ros-${ROS_DISTRO_REQUIRED}-ament-lint-auto
  ros-${ROS_DISTRO_REQUIRED}-ament-lint-common
  ros-${ROS_DISTRO_REQUIRED}-rosidl-default-generators
  ros-${ROS_DISTRO_REQUIRED}-rosidl-default-runtime
)

if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_CYAN=$'\033[36m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_CYAN=""
fi

section() { printf '\n%s%s%s\n' "$C_BOLD" "$1" "$C_RESET"; }
ok()      { printf '  %s[ ok ]%s %s\n' "$C_GREEN" "$C_RESET" "$1"; }
missing() { printf '  %s[miss]%s %s\n' "$C_YELLOW" "$C_RESET" "$1"; }
fail()    { printf '  %s[fail]%s %s\n' "$C_RED" "$C_RESET" "$1"; }
info()    { printf '  %s%s%s\n' "$C_DIM" "$1" "$C_RESET"; }
die()     { printf '\n%serror:%s %s\n\n' "$C_RED" "$C_RESET" "$1" >&2; exit 1; }

rule() {
  printf '%s%s%s\n' "$C_CYAN" "==================================================================" "$C_RESET"
}

CHECK_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1 ;;
    *) die "unrecognised argument '$1'. Usage: ./requirements.sh [--check]" ;;
  esac
  shift
done

printf '\n'
rule
printf '  %sbenzene robot | task dependency installer%s\n' "$C_BOLD" "$C_RESET"
rule

section "Checking the system"

[ -r /etc/os-release ] || die "cannot read /etc/os-release; this is not a supported system."
. /etc/os-release

if [ "${ID:-}" != "ubuntu" ]; then
  die "This task requires Ubuntu. Other distributions are not supported."
fi

ok "Ubuntu $VERSION_ID ($VERSION_CODENAME)"

apt_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"
}

apt_available() {
  local candidate
  candidate=$(apt-cache policy "$1" 2>/dev/null | awk '/Candidate:/ {print $2}')
  [ -n "$candidate" ] && [ "$candidate" != "(none)" ]
}

# --- Establish Sudo and Apt setup early so we can use it for ROS 2 repo installation ---
APT_UPDATED=0
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 || die "sudo is not installed, and this is not running as root."
  SUDO="sudo"
fi

apt_update_once() {
  [ "$APT_UPDATED" -eq 1 ] && return 0
  info "refreshing the package lists..."
  $SUDO apt-get update -qq || die "apt-get update failed. Check your network connection."
  APT_UPDATED=1
}

if [ "$CHECK_ONLY" -eq 0 ]; then
  if [ -n "$SUDO" ]; then
    info "apt needs root; you may be asked for your password."
    $SUDO -v || die "could not obtain sudo privileges."
  fi
  apt_update_once
fi

TO_INSTALL=()
UNAVAILABLE=()

section "ROS 2 Prerequisites"

if [ -d "/opt/ros/$ROS_DISTRO_REQUIRED" ]; then
  ok "/opt/ros/$ROS_DISTRO_REQUIRED exists"
else
  missing "/opt/ros/$ROS_DISTRO_REQUIRED does not exist -- ROS 2 is not installed."

  if [ "$CHECK_ONLY" -eq 0 ]; then
    info "Automatically setting up the ROS 2 $ROS_DISTRO_REQUIRED repository..."

    $SUDO apt-get install -y curl software-properties-common
    $SUDO add-apt-repository universe -y
    $SUDO curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $VERSION_CODENAME main" | $SUDO tee /etc/apt/sources.list.d/ros2.list > /dev/null

    # Force an apt update so the new repository is read
    APT_UPDATED=0
    apt_update_once
  else
    info "Run without --check to automatically configure the ROS 2 repository."
  fi

  # Ensure the base ROS 2 package gets checked and installed below
  ROS_PACKAGES_EXPECTED+=("ros-${ROS_DISTRO_REQUIRED}-ros-base")
fi

survey_group() {
  local label="$1"; shift
  section "$label"
  local pkg
  for pkg in "$@"; do
    if apt_installed "$pkg"; then
      ok "$pkg"
    elif apt_available "$pkg"; then
      missing "$pkg"
      TO_INSTALL+=("$pkg")
    else
      fail "$pkg -- not found in any configured apt repository"
      UNAVAILABLE+=("$pkg")
    fi
  done
}

survey_group "ROS 2 Benzene Dependencies" "${ROS_PACKAGES_EXPECTED[@]}"
survey_group "System & Python Modules" "${SYSTEM_PACKAGES[@]}"
survey_group "Build Tools" "${BUILD_PACKAGES[@]}"

section "Summary"

if [ "${#UNAVAILABLE[@]}" -gt 0 ]; then
  fail "${#UNAVAILABLE[@]} package(s) could not be found in any configured repository:"
  for pkg in "${UNAVAILABLE[@]}"; do
    info "  $pkg"
  done
  die "Your apt lists may be stale or missing repositories. Try checking your sources."
fi

if [ "${#TO_INSTALL[@]}" -eq 0 ]; then
  ok "nothing to install -- every task dependency is already present"
else
  printf '  %d package(s) to install:\n' "${#TO_INSTALL[@]}"
  for pkg in "${TO_INSTALL[@]}"; do
    info "  $pkg"
  done

  if [ "$CHECK_ONLY" -eq 1 ]; then
    printf '\n  would run: %s apt-get install -y %s\n' "$SUDO" "${TO_INSTALL[*]}"
    printf '  %sRun without --check to install them.%s\n\n' "$C_DIM" "$C_RESET"
    exit 0
  fi

  section "Installing"
  if ! $SUDO apt-get install -y "${TO_INSTALL[@]}"; then
    die "apt-get install failed."
  fi
  ok "packages installed"
fi

printf '\n'
ok "All dependencies are ready for the Benzene robot!"
printf '\n'