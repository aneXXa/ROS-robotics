# ROS-robotics

WSL2, Ubuntu 26.04, ROS 2 **lyrical**. Kit: `v1-w03`.

## ПР03 — нода `patrol`

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
colcon build --symlink-install --packages-select patrol turtle_bringup
source install/setup.bash
```

Терминал A: `ros2 launch turtle_bringup sim.launch.py`  
Терминал B:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Без remap команда уходит в `/cmd_vel` и turtlesim её не видит.

```bash
python3 -m pytest src/patrol/test -v
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

## ПР02

Пакет `turtle_bringup`, launch `sim.launch.py`. См. `evidence/pr02/`.

## ПР01

Домены 16/17, turtlesim + teleop. См. `evidence/pr01/`.
