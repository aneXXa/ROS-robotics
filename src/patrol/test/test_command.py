"""Тесты команды и проверки параметров."""

import math

from geometry_msgs.msg import Twist

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


def test_no_pose_yields_zero_twist() -> None:
    cmd = command_from_pose(None)
    assert isinstance(cmd, Twist)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_pose_uses_speeds() -> None:
    pose = Pose()
    pose.x = 1.0
    cmd = command_from_pose(pose, linear_speed=0.4, turn_rate=-0.2)
    assert cmd.linear.x == 0.4
    assert cmd.angular.z == -0.2


def test_publish_hz_accepts_5() -> None:
    assert validate_publish_hz(5.0) == 5.0
    assert timer_period_sec(5.0) == 0.2


def test_publish_hz_10_to_5_period() -> None:
    assert validate_publish_hz(10.0) == 10.0
    assert timer_period_sec(10.0) == 0.1
    assert validate_publish_hz(5.0) == 5.0
    assert timer_period_sec(5.0) == 0.2


def test_publish_hz_rejects_zero() -> None:
    assert validate_publish_hz(0.0) is None


def test_publish_hz_rejects_negative() -> None:
    assert validate_publish_hz(-1.0) is None


def test_publish_hz_rejects_nan() -> None:
    assert validate_publish_hz(math.nan) is None


def test_linear_and_turn_bounds() -> None:
    assert validate_linear_speed(0.0) == 0.0
    assert validate_linear_speed(1.0) == 1.0
    assert validate_linear_speed(1.1) is None
    assert validate_turn_rate(-1.0) == -1.0
    assert validate_turn_rate(1.0) == 1.0
    assert validate_turn_rate(1.5) is None
    assert validate_turn_rate(math.nan) is None
