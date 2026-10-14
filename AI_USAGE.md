# Декларация использования ИИ

## PR03

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: пакет `patrol`, `evidence/pr03/*`, README, CI
- Характер помощи: каркас ноды, чистая функция, тесты, demo, CI под kit v1-w03
- Проверка: pytest, colcon build, topic info без/с remap, topic hz ≈ 10 Hz

## PR04

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: параметры и валидация в `patrol`, `evidence/pr04/*`, CI под kit v1-w04
- Характер помощи: `declare_parameter` + callback, recreate таймера, тесты 0/neg/NaN/10→5, parameters.md
- Проверка: pytest 8 passed; `param set` 5.0 → hz≈5; `param set` 0.0 отклонён; `/clear`; `action list` → `rotate_absolute`

## PR05

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: `course_bringup` (launch, pose_relay, pose_subscriber), `evidence/pr05/*`, CI kit v1-w06
- Характер помощи: namespace/remap/IfCondition record, QoS best_effort vs reliable, MCAP bag + replay overrides
- Проверка: launch `/robot_a`; qos-before incompatible; qos-after + bag info один топик; replay best_effort ок

## PR06

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: `course_description` (Xacro/URDF, display.launch), `evidence/pr06/*`, CI
- Характер помощи: параметризованная модель Ackermann, tf_static QoS, тест parent lidar, дефект camera_link
- Проверка: check_urdf; pytest parent=base_link; tf-qos transient_local vs volatile; tf2_echo 0.28/0.38
