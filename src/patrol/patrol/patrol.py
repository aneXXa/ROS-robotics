"""Нода patrol: подписка на позу, таймер 0.1 с, публикация Twist в cmd_vel."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose  # type: ignore

from patrol.command import command_from_pose


class Patrol(Node):
    def __init__(self) -> None:
        super().__init__('patrol')
        self._last_pose: Pose | None = None
        self._pose_sub = self.create_subscription( # TASK - subscrube to turtle1/pose
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(0.1, self._on_timer)

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(command_from_pose(self._last_pose))


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
