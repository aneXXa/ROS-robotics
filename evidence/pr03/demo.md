# PR03: нода patrol

## Нода

Подписка на `/turtle1/pose` только кладёт сообщение в поле.
Таймер 0.1 с публикует `Twist` в относительный `cmd_vel`.
До первой позы — нули; потом `linear.x=0.5`, `angular.z=0.3`
(`command_from_pose`).

## init / spin / callback / Ctrl+C

- `rclpy.init()` — контекст ROS для создания процесса. Подготовка среды.
- `Patrol()` — нода, подписка, publisher, таймер. Участник графа.
- `rclpy.spin(node)` — главный цикл. Пока работает spin (получение информации из cmd) - работает нода.
- `_on_pose` — сохраняет последнюю позу.
- `_on_timer` — считает Twist и публикует.
- `Ctrl+C` → выход из spin, `destroy_node`, `shutdown`.
  После убийства процесса turtlesim гасит скорость,
  перестают приходить ненулевые `cmd_vel`. После остановки patrol
  скорости стали 0 (см. pose-after-stop).

## Сбой: относительный `cmd_vel`

```bash
ros2 run patrol patrol
```

`cmd_vel` без remap → `/cmd_vel`, а не `/turtle1/cmd_vel`. Издатель то есть, но turtlesim на него не подписан.

| Топик | pub | sub |
| --- | --- | --- |
| `/cmd_vel` | 1 (patrol) записывает | 0 |
| `/turtle1/cmd_vel` | 0 | 1 (turtlesim) читает |

Черепаха не едет от patrol.

## Исправление: remap

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

`-r` - ремап. Сказано cmd_vel, но слушаем `\turtle1\cmd_vel` \
На `/turtle1/cmd_vel`: 1 pub (patrol) + 1 sub (turtlesim). Поза приходит.

Частота команды (~10 с): **≈ 10 Гц (таймер 0.1 с).**

```text
average rate: 10.000
```

## Запуск

```bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 launch turtle_bringup sim.launch.py
# другой терминал:
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```
