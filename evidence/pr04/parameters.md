# PR04: параметры patrol

Параметры: `linear_speed` (0–1), `turn_rate` (−1–1), `publish_hz` (1–30).
Проверка до смены таймера и кеша. Допустимый `publish_hz` →
`cancel` + `destroy_timer` + новый таймер с периодом `1/hz`.

## Запуск

```bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 run turtlesim turtlesim_node
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

## Defaults

```text
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 param get /patrol linear_speed
Double value is: 0.5
$ ros2 param get /patrol turn_rate
Double value is: 0.3
```

## 10 → 5 Гц

```text
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 topic hz /turtle1/cmd_vel
average rate: 5.000
```

Обратно на 10:

```text
$ ros2 param set /patrol publish_hz 10.0
Set parameter successful
$ ros2 topic hz /turtle1/cmd_vel
average rate: 9.999
```

## Отказ: publish_hz = 0 без проверки

`timer_period_sec(0.0)` → `ZeroDivisionError: division by zero`
(период = `1/publish_hz`). Состояние ноды ломается, если проверку отключить.

## Исправление: ноль / отриц. отклонены, частота 5 сохранена

```text
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite in [1, 30]
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 param set /patrol publish_hz -1.0
Setting parameter failed: publish_hz must be finite in [1, 30]
```

NaN в чистой функции: `validate_publish_hz(nan) is None` (pytest).
CLI `ros2 param set … nan` отвергает тип до колбэка.

## Service / action

```text
$ ros2 service call /clear std_srvs/srv/Empty
response: std_srvs.srv.Empty_Response()

$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Сервис `/clear` — разовый запрос/ответ: стёрли фон и готово.
Action `rotate_absolute` — цель с обратной связью и отменой, пока черепаха
доворачивается.

## Тесты

```bash
python3 -m pytest src/patrol/test -v
# 8 passed — см. tests.txt
```
