"""Чистая логика AckermannDrive → Twist для Gazebo AckermannSteering."""

from __future__ import annotations

import math
from dataclasses import dataclass


WHEEL_BASE_M = 0.8
MAX_SPEED_MPS = 1.2
MAX_STEER_RAD = 0.45
MAX_AGE_SEC = 0.25


@dataclass(frozen=True)
class TwistCommand:
    linear_x: float
    angular_z: float
    reason: str = ''


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def ackermann_to_twist(
    speed: float,
    steering_angle: float,
    *,
    age_sec: float | None = None,
) -> TwistCommand:
    """Преобразовать команду. Нечисловое / устаревшее → нули + reason."""
    if age_sec is not None and age_sec > MAX_AGE_SEC:
        return TwistCommand(0.0, 0.0, reason='stale_command')
    if not math.isfinite(speed) or not math.isfinite(steering_angle):
        return TwistCommand(0.0, 0.0, reason='non_finite')

    v = clamp(float(speed), 0.0, MAX_SPEED_MPS)
    delta = clamp(float(steering_angle), -MAX_STEER_RAD, MAX_STEER_RAD)
    if v == 0.0:
        return TwistCommand(0.0, 0.0)
    omega = v * math.tan(delta) / WHEEL_BASE_M
    return TwistCommand(v, omega)
