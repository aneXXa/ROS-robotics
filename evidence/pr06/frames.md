# PR06: дерево кадров

Владелец всех фиксированных преобразований: `robot_state_publisher`
(топик `/tf_static`). Подвижные колёса (`continuous`) появятся в `/tf`
только после публикации `/joint_states`.

| Joint | Parent | Child | Ожидаемое xyz (м) | Owner |
| --- | --- | --- | --- | --- |
| camera_link_joint | base_link | camera_link | 0.28, 0, 0.38 | robot_state_publisher |
| lidar_link_joint | base_link | lidar_link | 0.28, 0, 0.38 | robot_state_publisher |
| imu_link_joint | base_link | imu_link | 0.28, 0, 0.38 | robot_state_publisher |
| front_left_wheel_joint | base_link | front_left_wheel | 0.40, 0.31, 0 | joint_states → /tf |
| front_right_wheel_joint | base_link | front_right_wheel | 0.40, −0.31, 0 | joint_states → /tf |
| rear_left_wheel_joint | base_link | rear_left_wheel | −0.40, 0.31, 0 | joint_states → /tf |
| rear_right_wheel_joint | base_link | rear_right_wheel | −0.40, −0.31, 0 | joint_states → /tf |

Проверка: `tf2_echo base_link lidar_link` → Translation `[0.280, 0.000, 0.380]`.

Дефект: parent `lidar_link` = `camera_link` при том же offset даёт
`[0.560, 0.000, 0.760]` и падение `test_lidar_parent_is_base_link`.
