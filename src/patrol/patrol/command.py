"""Команда Twist из последней позы (чистая логика без ROS)."""

from __future__ import annotations

from geometry_msgs.msg import Twist

try:
    from turtlesim_msgs.msg import Pose # TASK
except ImportError:
    from turtlesim.msg import Pose  # type: ignore # TASK


def command_from_pose(pose: Pose | None) -> Twist:
    """До первой позы — нули; иначе патрульный Twist."""
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = 0.5
    cmd.angular.z = 0.3
    return cmd
