# ROS-robotics

Практикум ROS 2 (ПР01–ПР06). Среда: **WSL2**, Ubuntu 26.04, ROS 2 **lyrical**.

Course kit: `.course-kit/v1/VERSION` = `v1-w01`,
SHA-256 `57866a9c98fa3abdec27b35a180697ee680bfb0f05cc015970ce306d6d849fea`.

## ПР02 — пакет `turtle_bringup` и launch

Из **корня** репозитория (`cd "$(git rev-parse --show-toplevel)"`):

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST   # после source
```

Сборка:

```bash
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build.txt
```

Запуск (терминал A):

```bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

Перед запуском остановите старые `turtlesim`. В другом терминале:
`ros2 node list --no-daemon --spin-time 2` → `/turtlesim`.
Остановка: `Ctrl+C` в A (дочерний turtlesim завершается вместе с launch).

Команда движения (B), тот же домен:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Ошибочное имя `/cmd_vel` не доходит до подписчика; нужно `/turtle1/cmd_vel`.

### Проверки ПР02

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

## ПР01 — кратко

Домен 16, turtlesim + teleop, разрыв на домене 17. Evidence: `evidence/pr01/`.

## CI

`.github/workflows/ci.yml` — course kit, сборка `turtle_bringup`, проверка
установленного `sim.launch.py`, `check_practice.py PR02`.
