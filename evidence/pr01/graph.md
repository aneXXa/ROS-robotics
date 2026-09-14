# PR01: Граф ROS 2

[Среда](environment.json) · [ROS Doctor](doctor.txt) · [README](../../README.md)

Перед запуском в каждом терминале:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
```

`LOCALHOST` выставлен **после** `source`: хук Lyrical иначе снова ставит
`SUBNET`, а на этой WSL-сети multicast discovery часто не склеивает локальные
ноды. `--no-daemon` в проверках ниже исключает кэш `ros2`-daemon.

## Исправный граф (ROS_DOMAIN_ID=16)

| Терминал | Роль | Команда |
|---|---|---|
| A | симулятор | `ros2 run turtlesim turtlesim_node` |
| B | teleop | `ros2 run turtlesim turtle_teleop_key` |
| C | наблюдение | CLI ниже |

Все три — домен **16**. Стрелки в B двигают черепаху.

### Команды и вывод

```powershell
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim
```

`node list` показывает участников домена.
В списке нет временных CLI-нод `echo`/`hz`: они появляются только пока
идёт соответствующая команда.

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

Издатель `/turtle1/cmd_vel` — `/teleop_turtle`, подписчик — `/turtlesim`.
Teleop на позу не подписывается: для клавиатуры обратная связь по `/pose`
не нужна.

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

Тип Lyrical — `turtlesim_msgs/msg/Pose`.

```powershell
$ ros2 topic hz /turtle1/pose
WARNING: topic [/turtle1/pose] does not appear to be published yet
average rate: 62.513
        min: 0.015s max: 0.017s std dev: 0.00051s window: 62
…
average rate: 62.500
        min: 0.012s max: 0.021s std dev: 0.00059s window: 3439
```

Замер остановлен после ~55 с (окно 3439 ≈ 62.5 Гц).
Ориентир таймера turtlesim 16 мс ≈ 62.5 Гц; фактическая частота **62.500 Гц**.

### Схема основных потоков

```text
стрелки (фокус в терминале B)
        │
        ▼
  /teleop_turtle
        │  /turtle1/cmd_vel  [geometry_msgs/msg/Twist]
        ▼
  /turtlesim  ──► окно: движение и след
        │  /turtle1/pose  [turtlesim_msgs/msg/Pose]
        ├──► ros2 topic echo … --once
        └──► ros2 topic hz …
```

### Ноды и роли

| Нода | Роль |
|---|---|
| `/turtlesim` | Симулятор. Подписывается на `/turtle1/cmd_vel`, публикует `/turtle1/pose` и `/turtle1/color_sensor`. Сервисы spawn/kill/reset/clear/set_pen/teleport, action `/turtle1/rotate_absolute`. |
| `/teleop_turtle` | Читает клавиши терминала B и публикует `Twist` в `/turtle1/cmd_vel`. |

### Топики

| Топик | Тип | Издатель → получатель в этом опыте | Назначение |
|---|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | `/teleop_turtle` → `/turtlesim` | Линейная и угловая скорость |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | `/turtlesim` → CLI `echo` / `hz` | Положение, угол, скорости |
| `/turtle1/color_sensor` | `turtlesim_msgs/msg/Color` | `/turtlesim` → в опыте не использован | Цвет под черепахой |
| `/parameter_events` | `rcl_interfaces/msg/ParameterEvent` | обе ноды | События параметров |
| `/rosout` | `rcl_interfaces/msg/Log` | обе ноды | Служебный лог |

### Измеренная частота `/turtle1/pose`

| Параметр | Значение |
|---|---|
| Средняя частота | **62.500 Гц** (диапазон по ходу 62.486–62.513) |
| Длительность | ~55 с |
| Последнее окно | min 0.012 с, max 0.021 с, std 0.00059 с, 3439 сообщений |
| Вывод | Совпадает с таймером 16 мс; поза идёт и у неподвижной черепахи |

## Разрыв и восстановление связи

`POSE_TYPE` уже хранит `turtlesim_msgs/msg/Pose` со стадии выше. В чужом
домене CLI не узнает тип у издателя, поэтому тип передаётся явно.
Симулятор A не перезапускался и всё время оставался в домене 16.

### До (оба в домене 16)

| Участник | Домен | Виден из C (16) |
|---|---|---|
| `/turtlesim` (A) | 16 | да |
| `/teleop_turtle` (B) | 16 | да |
| CLI (C) | 16 | обе ноды |

Управление работает. Поза приходит.

### Сбой (teleop и CLI в домене 17)

В B: `Ctrl+C`, затем:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

В C:

```powershell
$ export ROS_DOMAIN_ID=17
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=124
```

Содержимое [pose-broken.txt](pose-broken.txt): только `!rclpy.ok()` —
`timeout` оборвал ожидание, сообщения Pose не было.

| Участник | Домен | Виден из C (17) |
|---|---|---|
| `/turtlesim` (A) | 16 | нет |
| `/teleop_turtle` (B) | 17 | да |
| CLI (C) | 17 | только `/teleop_turtle` |

Стрелки не двигают черепаху: `cmd_vel` публикуется в домене 17, подписчик
симулятора слушает домен 16. Издателя `/turtle1/pose` в 17 нет.

### После (teleop снова в домене 16)

```powershell
$ export ROS_DOMAIN_ID=16
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=0
```

[pose-fixed.txt](pose-fixed.txt) — одно сообщение Pose
(`x≈0.45`, `y≈6.53`, `theta≈-2.13`, скорости 0). Стрелки снова двигают черепаху.

| Участник | Домен | Виден из C (16) |
|---|---|---|
| `/turtlesim` (A) | 16 | да |
| `/teleop_turtle` (B) | 16 | да |
| CLI (C) | 16 | обе ноды |

### Сравнение до / сбой / после

| Проверка | Исправно | Разрыв | Восстановлено |
|---|---|---|---|
| Домен A / B / C | 16 / 16 / 16 | 16 / 17 / 17 | 16 / 16 / 16 |
| Ноды, видимые в C | teleop и turtlesim | только teleop | teleop и turtlesim |
| `topic echo` позы в C | поза получена | таймаут 5 с | поза в `pose-fixed.txt` |
| Код `timeout` | — | **124** | **0** |
| Управление стрелками | работает | не работает | работает |
| Файл | — | [pose-broken.txt](pose-broken.txt) | [pose-fixed.txt](pose-fixed.txt) |
