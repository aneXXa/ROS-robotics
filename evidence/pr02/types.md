# PR02: Типы топиков turtlesim

Среда: ROS 2 **lyrical**. Тип позы по `ros2 topic type /turtle1/pose`:
`turtlesim_msgs/msg/Pose` (не Jazzy `turtlesim/msg/Pose`).

## Два основных топика

| Топик | Тип | Назначение |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команда скорости: издатель → `/turtlesim` |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | Состояние черепахи: `/turtlesim` → подписчики |

## Поля `geometry_msgs/msg/Twist`

По `ros2 interface show geometry_msgs/msg/Twist`:

| Поле | Смысл в turtlesim |
|---|---|
| `linear.x` | Скорость вперёд вдоль текущего курса (м/с в единицах сима) |
| `linear.y`, `linear.z` | В 2D turtlesim не используются (обычно 0) |
| `angular.x`, `angular.y` | Не используются (обычно 0) |
| `angular.z` | Угловая скорость вокруг вертикали; `> 0` — против часовой (увеличивает `theta`) |

В опыте: `{linear: {x: 1.0}, angular: {z: 0.5}}` — вперёд и лёгкий поворот влево (CCW).

## Поля `turtlesim_msgs/msg/Pose`

| Поле | Смысл |
|---|---|
| `x`, `y` | Координаты на плоскости |
| `theta` | Ориентация (рад) |
| `linear_velocity`, `angular_velocity` | Текущие скорости; без новых `cmd_vel` становятся 0 |

Имя топика должно совпасть **точно**: тип `Twist` на `/cmd_vel` не доходит
до подписчика `/turtle1/cmd_vel`.
