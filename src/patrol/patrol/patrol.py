"""Нода patrol: поза, параметры скорости/частоты, Twist в cmd_vel."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from rclpy.parameter import Parameter

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose  # type: ignore

from patrol.command import (
    command_from_pose,
    timer_period_sec,
    validate_linear_speed,
    validate_publish_hz,
    validate_turn_rate,
)


class Patrol(Node):
    def __init__(self) -> None:
        super().__init__('patrol')
        self.declare_parameter('linear_speed', 0.5) #TASK4
        self.declare_parameter('turn_rate', 0.3) #TASK4
        self.declare_parameter('publish_hz', 10.0) #TASK4

        self._linear_speed = float(self.get_parameter('linear_speed').value)
        self._turn_rate = float(self.get_parameter('turn_rate').value)
        self._publish_hz = float(self.get_parameter('publish_hz').value)

        self._last_pose: Pose | None = None
        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(
            timer_period_sec(self._publish_hz),
            self._on_timer,
        )
        self.add_on_set_parameters_callback(self._on_set_parameters)

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(
            command_from_pose(
                self._last_pose,
                self._linear_speed,
                self._turn_rate,
            )
        )

    def _restart_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self.destroy_timer(self._timer)
        self._timer = self.create_timer(
            timer_period_sec(self._publish_hz),
            self._on_timer,
        )

    def _on_set_parameters(self, params: list[Parameter]) -> SetParametersResult:
        new_linear = self._linear_speed
        new_turn = self._turn_rate
        new_hz = self._publish_hz

        for param in params:
            if param.name == 'linear_speed':
                parsed = validate_linear_speed(param.value)
                if parsed is None:
                    return SetParametersResult(
                        successful=False,
                        reason='linear_speed must be finite in [0, 1]',
                    )
                new_linear = parsed
            elif param.name == 'turn_rate':
                parsed = validate_turn_rate(param.value)
                if parsed is None:
                    return SetParametersResult(
                        successful=False,
                        reason='turn_rate must be finite in [-1, 1]',
                    )
                new_turn = parsed
            elif param.name == 'publish_hz':
                parsed = validate_publish_hz(param.value)
                if parsed is None:
                    return SetParametersResult(
                        successful=False,
                        reason='publish_hz must be finite in [1, 30]',
                    )
                new_hz = parsed

        hz_changed = new_hz != self._publish_hz
        self._linear_speed = new_linear
        self._turn_rate = new_turn
        self._publish_hz = new_hz
        if hz_changed:
            self._restart_timer()
        return SetParametersResult(successful=True)


def main() -> None:
    rclpy.init()
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
