# PR02: Команды Linux и launch turtle_bringup

Среда: WSL2, Ubuntu 26.04, ROS 2 **lyrical**, `ROS_DOMAIN_ID=16`.
Корень workspace: `/home/nexxa/ROS-robotics`.

## Использованные команды

| № | Команда | Назначение | Результат |
|---|---|---|---|
| 1 | `pwd` | Абсолютный путь текущего каталога; проверка, что терминал в корне репозитория | `/home/nexxa/ROS-robotics` |
| 2 | `mkdir -p src evidence/pr02` | Создаёт каталоги (в т.ч. вложенные); `-p` не падает, если они уже есть | созданы `src/`, `evidence/pr02/` |
| 3 | `printenv ROS_DISTRO ROS_DOMAIN_ID` и `ros2 pkg prefix turtlesim` | `printenv` — переменные текущего shell после `source`/`export`; `pkg prefix` — путь установленного пакета | `lyrical`, `16`, `/opt/ros/lyrical` |

## Чем `>` отличается от `|`

| Оператор | Что делает | Пример |
|---|---|---|
| `>` | Перенаправляет **stdout в файл**. Старое содержимое файла **затирается**. Следующей команде данные не передаются. | `ros2 topic echo /turtle1/pose --once > evidence/pr02/pose.txt` |
| `\|` | Передаёт **stdout следующей команде** (конвейер). Файл сам по себе не создаёт. | `ros2 topic list \| grep turtle` |

Кратко:

- `>` — «записать вывод в файл»;
- `|` — «передать вывод другой программе».

Часто вместе с `>` используют `2>&1`: направить **stderr** туда же, куда
уже ушёл stdout. В этой работе:

## Чем `source` отличается от запуска новой программы

| Действие | Что происходит |
|---|---|
| `source /opt/ros/lyrical/setup.bash` (или `. setup.bash`) | Скрипт выполняется в текущем** shell. `export`, `PATH`, `ROS_*` остаются после окончания скрипта. |
| `bash /opt/ros/lyrical/setup.bash` или `./setup.bash` | Запускается дочерний процесс. Переменные задаются только внутри него и исчезают, когда процесс завершился. Родительский терминал ROS не получает. |


## Пакет и сборка

Создан пустой пакет:

```bash
cd src
ros2 pkg create --build-type ament_python --license Apache-2.0 \
  turtle_bringup --dependencies launch launch_ros turtlesim
```

Первая сборка (без установленного launch) → [build-empty.txt](build-empty.txt):

```bash
Starting >>> turtle_bringup
Finished <<< turtle_bringup …
Summary: 1 package finished …
```

После `source install/setup.bash`:

```bash
$ ros2 pkg prefix turtle_bringup
/home/nexxa/ROS-robotics/install/turtle_bringup
```

Путь ведёт в `install` workspace, не в `/opt/ros/lyrical`. Пустой пакет
найден, своей ноды ещё нет.

Добавлены `launch/sim.launch.py` и запись в `setup.py` (`glob('launch/*.launch.py')`).
Повторная сборка → [build.txt](build.txt).

```bash
$ ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
sim.launch.py
```

---

## Запуск, проверка графа, остановка

### Терминал A — launch

```bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtle_bringup
# → /home/nexxa/ROS-robotics/install/turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
# → sim.launch.py
ros2 launch turtle_bringup sim.launch.py
```

Фрагмент вывода A (один процесс, одно окно):

```bash
[INFO] [turtlesim_node-1]: process started with pid [12051]
[turtlesim_node-1] … Starting turtlesim with node name /turtlesim
[turtlesim_node-1] … Spawning turtle [turtle1] …
```

### Терминал B — проверка графа

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
```

Результат — одна нода:

```text
/turtlesim
```

### Остановка Ctrl+C

В A:

```bash
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[turtlesim_node-1] … signal_handler(signum=2)
[INFO] [turtlesim_node-1]: process has finished cleanly [pid 12051]
```

Launch завершил и себя, и дочерний `turtlesim_node`.

`ros2 launch` только стартует действие `Node` из `sim.launch.py`
(`package='turtlesim'`, `executable='turtlesim_node'` — как у `ros2 run`).

## 4. Команда → движение

Launch оставлен в A. Teleop остановлен. В C (после `source` и домена 16):

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
```

Тип позы: `turtlesim_msgs/msg/Pose`.

Ожидаем: для `{linear: {x: 1.0}, angular: {z: 0.5}}`:
черепаха едет вперёд по курсу и поворачивает против часовой. Одна публикация `--once` — короткий импульс, не вечное
движение: без новых сообщений turtlesim останавливает скорость.

**Поза до** (старт сима, терминал C):

```bash
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

В B:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Вывод: `publishing #1: … Twist(linear=… x=1.0 …, angular=… z=0.5)`.

Файлы: [pose-before.txt](pose-before.txt), [pose-after-once.txt](pose-after-once.txt)
(повторный замер импульса `--once` на том же типе/топике).

## 5. Ошибка имени топика и исправление

### Сбой — публикация в `/cmd_vel`

В B (только имя топика изменено; скорость и домен те же):

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`--wait-matching-subscriptions 0` нужен, иначе `--once` ждал бы подписчика
на несуществующем (для turtlesim) имени. Издатель печатал `publishing #1…`,
но черепаха от этого топика не управлялась.

Пока издатель работал, в C:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

| Топик | Publisher count | Subscription count | Кто |
|---|---|---|---|
| `/cmd_vel` | **1** (`_ros2cli_…`) | **0** | тип Twist тот же, подписчика turtlesim нет |
| `/turtle1/cmd_vel` | **0** | **1** (`turtlesim`) | симулятор ждёт другое **имя** |

Файлы: [topic-info-wrong.txt](topic-info-wrong.txt),
[topic-info-turtle1-during-wrong.txt](topic-info-turtle1-during-wrong.txt).

После `Ctrl+C` у ошибочного издателя `/cmd_vel` исчезает из графа
(`Unknown topic`), а `/turtle1/cmd_vel` по-прежнему имеет только подписку
turtlesim (0 издателей) — как в терминале C после остановки.

### После — только `/cmd_vel` → `/turtle1/cmd_vel`

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Черепаха снова поехала. Издатель и
подписчик на одном имени. После `Ctrl+C` движение прекратилось.

### Сравнение до / сбой / после

| | До (правильно) | Сбой | После |
|---|---|---|---|
| Топик издателя | `/turtle1/cmd_vel` | `/cmd_vel` | `/turtle1/cmd_vel` |
| Тип | `geometry_msgs/msg/Twist` | тот же | тот же |
| Подписчик turtlesim | да | нет на этом имени | да |
| Движение | да (`--once` / rate) | нет от ошибочного топика | да |
| `topic info` | 1 sub на `/turtle1/cmd_vel` | 1 pub на `/cmd_vel`, 0 sub; 0 pub / 1 sub на `/turtle1/cmd_vel` | издатель на `/turtle1/cmd_vel` |

### Почему правильного типа недостаточно

Сопоставление в ROS 2 идёт по полному имени топика и типу вместе.
`Twist` на `/cmd_vel` и `Twist` на `/turtle1/cmd_vel` — разные каналы.
Симулятор подписан только на `/turtle1/cmd_vel`; совпадение типа без
совпадения имени не соединяет конечные точки.

Подробнее поля сообщений: [types.md](types.md).

