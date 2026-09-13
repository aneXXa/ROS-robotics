# ROS-robotics

Практикум ROS 2 (ПР01–ПР06). Среда ПР01: **WSL2**, Ubuntu 26.04, ROS 2 **lyrical**.

Course kit: `.course-kit/v1/VERSION` = `v1-w01`,
SHA-256 архива `57866a9c98fa3abdec27b35a180697ee680bfb0f05cc015970ce306d6d849fea`.

## ПР01 — порядок запуска

Новый терминал. `source` сначала, домен и discovery — **после** него
(хук ROS в этом дистрибутиве перезаписывает `ROS_AUTOMATIC_DISCOVERY_RANGE` в `SUBNET`).

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
```

Три терминала с одинаковыми переменными:

| Терминал | Команда |
|---|---|
| A | `ros2 run turtlesim turtlesim_node` |
| B | `ros2 run turtlesim turtle_teleop_key` — фокус здесь, стрелки |
| C | наблюдение CLI |

Проверка исправного графа (C):

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose   # ≥10 с, ориентир ~62.5 Гц, Ctrl+C
```

Тип позы в Lyrical: `turtlesim_msgs/msg/Pose`. Команда движения: `/turtle1/cmd_vel`.

Разрыв связи: в B остановить teleop, `export ROS_DOMAIN_ID=17`, запустить teleop снова.
A не трогать (остаётся в 16). В C:

```bash
export ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидается только `/teleop_turtle`, exit=124.

Восстановление: в B снова teleop с `ROS_DOMAIN_ID=16`. В C то же с доменом 16 и `pose-fixed.txt`. Ожидаются обе ноды, exit=0.

## Проверки ПР01

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

Своего пакета и `colcon` в ПР01 нет.

## CI

`.github/workflows/ci.yml` — валидация `environment.json`, загрузка course kit по SHA-256, `check_practice.py PR01`.
