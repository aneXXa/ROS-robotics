"""Тесты чистой функции command_from_pose."""

from geometry_msgs.msg import Twist

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose  # type: ignore

from patrol.command import command_from_pose


def test_no_pose_yields_zero_twist() -> None:
    cmd = command_from_pose(None)
    assert isinstance(cmd, Twist)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_pose_yields_patrol_twist() -> None:
    pose = Pose()
    pose.x = 1.0
    pose.y = 2.0
    pose.theta = 0.5
    cmd = command_from_pose(pose)
    assert cmd.linear.x == 0.5
    assert cmd.angular.z == 0.3
