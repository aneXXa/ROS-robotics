# PR01: Граф ROS 2

## Исправный граф (ROS_DOMAIN_ID=16)

Среда наблюдения: `source /opt/ros/lyrical/setup.bash`, затем
`ROS_DOMAIN_ID=16`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`.
Терминал A — `ros2 run turtlesim turtlesim_node`.
Терминал B — `ros2 run turtlesim turtle_teleop_key` (фокус на B, стрелки).
Терминал C — команды ниже.

### Команды и вывод

```powershell
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim
```

```powershell
$ ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim_msgs/msg/Color]
/turtle1/pose [turtlesim_msgs/msg/Pose]
```

```powershell
$ ros2 node info /turtlesim
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim_msgs/msg/Color
    /turtle1/pose: turtlesim_msgs/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim_msgs/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim_msgs/srv/Spawn
    /turtle1/set_pen: turtlesim_msgs/srv/SetPen
    /turtle1/teleport_absolute: turtlesim_msgs/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim_msgs/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim_msgs/action/RotateAbsolute
  Action Clients:
```

```powershell
$ ros2 topic type /turtle1/pose
turtlesim_msgs/msg/Pose

$ POSE_TYPE=$(ros2 topic type /turtle1/pose)
$ ros2 topic echo /turtle1/pose --once
x: 4.486705303192139
y: 5.518413066864014
theta: -2.923185348510742
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Черепаха неподвижна (`linear_velocity` / `angular_velocity` = 0), поза всё равно публикуется.

```text
$ ros2 topic hz /turtle1/pose
WARNING: topic [/turtle1/pose] does not appear to be published yet
average rate: 62.513
        min: 0.015s max: 0.017s std dev: 0.00051s window: 62
average rate: 62.500
        min: 0.012s max: 0.021s std dev: 0.00059s window: 3439
```

Замер: ~55 с (окно 3439 сообщений / 62.5 Гц). \
Фактическая частота: **62.500 Гц** (диапазон по ходу замера 62.486–62.513 Гц).
Ориентир turtlesim — таймер 16 мс ≈ 62.5 Гц.

### Ноды и роли

| Нода | Роль |
|---|---|
| `/turtlesim` | Симулятор. Подписывается на команду движения `/turtle1/cmd_vel`, публикует позу `/turtle1/pose` и цвет `/turtle1/color_sensor`. Сервисы spawn/kill/reset/clear/set_pen/teleport, action `/turtle1/rotate_absolute`. |
| `/teleop_turtle` | Клавиатурное управление. Публикует `geometry_msgs/msg/Twist` в `/turtle1/cmd_vel`, пока фокус в терминале B. |

### Топики (полные имена и типы)

| Топик | Тип | Назначение |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команда движения: `/teleop_turtle` → `/turtlesim` |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | Поза черепахи (Lyrical; не `turtlesim/msg/Pose`) |
| `/turtle1/color_sensor` | `turtlesim_msgs/msg/Color` | Цвет под черепахой |
| `/parameter_events` | `rcl_interfaces/msg/ParameterEvent` | События параметров |
| `/rosout` | `rcl_interfaces/msg/Log` | Лог |

### Измеренная частота `/turtle1/pose`

- **62.500 Гц**
- Длительность замера: **~55 с**
- Последнее окно: min 0.012 с, max 0.021 с, std 0.00059 с, 3439 сообщений
- Совпадает с таймером turtlesim 16 мс

## Разрыв и восстановление связи

### До (оба в домене 16)

| Участник | Домен | Виден в графе 16 |
|---|---|---|
| `/turtlesim` (A) | 16 | да |
| `/teleop_turtle` (B) | 16 | да |
| CLI (C) | 16 | видит обе ноды |

Стрелки в B двигают черепаху. Поза приходит (`pose` echo, exit=0).

### Сбой (teleop и CLI в домене 17)

В B: Ctrl+C, `export ROS_DOMAIN_ID=17`, снова `ros2 run turtlesim turtle_teleop_key`.
В C:

```powershell
$ export ROS_DOMAIN_ID=17
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=124
```

`pose-broken.txt`: `!rclpy.ok()` — `timeout` оборвал ожидание, сообщение не пришло.

| Участник | Домен | Виден из C (17) |
|---|---|---|
| `/turtlesim` (A) | 16 | нет |
| `/teleop_turtle` (B) | 17 | да |
| CLI (C) | 17 | только `/teleop_turtle` |

Стрелки не двигают черепаху: `cmd_vel` уходит в домен 17, подписчик симулятора слушает домен 16. Позы в 17 нет — издатель `/turtle1/pose` остался в 16. Тип пришлось передать явно (`$POSE_TYPE`): в чужом домене CLI не узнает его у издателя.

### После (teleop снова в домене 16)

В B: Ctrl+C, `export ROS_DOMAIN_ID=16`, снова teleop.
В C:

```text
$ export ROS_DOMAIN_ID=16
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=0
```

`pose-fixed.txt` — одно сообщение `turtlesim_msgs/msg/Pose` (черепаха неподвижна, скорости 0). Стрелки снова двигают черепаху.

| Участник | Домен | Виден из C (16) |
|---|---|---|
| `/turtlesim` (A) | 16 | да |
| `/teleop_turtle` (B) | 16 | да |
| CLI (C) | 16 | обе ноды |

### Коды возврата

| Файл | Домен CLI | Ноды | Поза | exit |
|---|---|---|---|---|
| `evidence/pr01/pose-broken.txt` | 17 | только `/teleop_turtle` | нет (`!rclpy.ok()`) | **124** (таймаут 5 с) |
| `evidence/pr01/pose-fixed.txt` | 16 | `/teleop_turtle`, `/turtlesim` | да | **0** |
