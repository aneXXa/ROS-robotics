"""Команда Twist и проверка параметров patrol (чистая логика)."""

from __future__ import annotations

import math

from geometry_msgs.msg import Twist

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose  # type: ignore


def command_from_pose(
    pose: Pose | None,
    linear_speed: float = 0.5,
    turn_rate: float = 0.3,
) -> Twist:
    """До первой позы — нули; иначе Twist из параметров скорости."""
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = float(linear_speed)
    cmd.angular.z = float(turn_rate)
    return cmd


def validate_linear_speed(value: float) -> float | None:
    """Допустимо: конечное число в [0, 1]. Иначе None — не менять состояние."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    value = float(value)
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        return None
    return value


def validate_turn_rate(value: float) -> float | None:
    """Допустимо: конечное число в [-1, 1]."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    value = float(value)
    if not math.isfinite(value) or value < -1.0 or value > 1.0:
        return None
    return value


def validate_publish_hz(value: float) -> float | None:
    """Допустимо: конечное число в [1, 30]. Ноль / NaN / отриц. — отклонить."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    value = float(value)
    if not math.isfinite(value) or value < 1.0 or value > 30.0:
        return None
    return value


def timer_period_sec(publish_hz: float) -> float:
    """Период таймера. Вызывать только после validate_publish_hz."""
    return 1.0 / publish_hz
