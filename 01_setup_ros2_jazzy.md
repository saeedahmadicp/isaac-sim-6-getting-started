# One-time setup: ROS 2 Jazzy on Ubuntu 24.04

**Isaac Sim does not need this.** 6.1 ships its own ROS 2 Jazzy libraries (`exts/isaacsim.ros2.core/jazzy`)
and loads them automatically. Install system ROS 2 only for the tools you run **outside** Isaac Sim,
which the course uses in lessons 1.4, 4.1 and 4.3:

* `ros2 topic list / echo / pub`
* `rviz2`
* `teleop_twist_keyboard`

NVIDIA's original course installs **Humble** on Ubuntu 22.04. This adaptation's reference setup is
**Ubuntu 24.04**, which pairs with **Jazzy**. If you are on Ubuntu 22.04, install Humble instead.

```bash
# 1. Locale + repo (official instructions: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
sudo apt update && sudo apt install -y software-properties-common curl
sudo add-apt-repository universe
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo $VERSION_CODENAME)_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# 2. ROS 2 Jazzy desktop (includes rviz2) + what the course uses
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-jazzy-teleop-twist-keyboard ros-jazzy-vision-msgs
```

Use it in **every new terminal** that talks to Isaac Sim:

```bash
source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp   # same RMW as Isaac Sim's default
ros2 topic list                               # with Isaac Sim playing a ROS graph you should see its topics
```

## Rules of thumb

* Keep `ROS_DOMAIN_ID` the same (or unset) in Isaac Sim's terminal and your ROS terminals.
* ROS topics only exist **while the simulation is playing**. Press Play first.
* To use your **system** Jazzy inside Isaac Sim (e.g. custom message packages), `source /opt/ros/jazzy/setup.bash`
  **before** running `./isaac-sim.sh`. Never try to fix `LD_LIBRARY_PATH` in an already running Isaac Sim;
  close it and relaunch from a correctly sourced terminal.
