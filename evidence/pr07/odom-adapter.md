# PR07: нормализация одометрии

## Frames

| Поле | Исходное (Gazebo / bridge) | Нормализованное |
| --- | --- | --- |
| `header.frame_id` | `course_ackermann/odom` | `odom` |
| `child_frame_id` | `course_ackermann/base_link` | `base_link` |

Вход bridge: `/vehicle/odom_gz` (`GZ_TO_ROS` с `/model/course_ackermann/odometry`).
Выход адаптера: `/vehicle/odom` + единственный dynamic tf `odom→base_link`.

Stamp, pose, twist и обе covariance копируются без изменений.
Сообщения с другими frames или нечисловыми значениями отклоняются.

## Владельцы tf

| Связь | Владелец |
| --- | --- |
| fixed: `base_link` → camera/lidar/imu | `robot_state_publisher` → `/tf_static` |
| dynamic: `odom` → `base_link` | `odom_adapter` → `/tf` |

Два издателя одной dynamic-связи не допускаются.

## Тест stamp

Модульный контракт frames: `test_odom_frames.py`.
На живом запуске: `ros2 topic echo /vehicle/odom --once` и
`ros2 run tf2_ros tf2_echo odom base_link --ros-args -p use_sim_time:=true`
должны совпадать по положению; stamp берётся из симуляции (`/clock`).
