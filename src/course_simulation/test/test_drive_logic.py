"""Модульные тесты Ackermann → Twist."""

import math

from course_simulation.drive_logic import ackermann_to_twist


def test_straight() -> None:
    cmd = ackermann_to_twist(0.8, 0.0)
    assert cmd.linear_x == 0.8
    assert abs(cmd.angular_z) < 1e-12
    assert cmd.reason == ''


def test_turn() -> None:
    cmd = ackermann_to_twist(1.0, 0.4)
    assert cmd.linear_x == 1.0
    assert abs(cmd.angular_z - (1.0 * math.tan(0.4) / 0.8)) < 1e-9


def test_zero_speed() -> None:
    cmd = ackermann_to_twist(0.0, 0.3)
    assert cmd.linear_x == 0.0
    assert cmd.angular_z == 0.0


def test_clamp_speed_and_steer() -> None:
    cmd = ackermann_to_twist(5.0, 1.0)
    assert cmd.linear_x == 1.2
    assert abs(cmd.angular_z - (1.2 * math.tan(0.45) / 0.8)) < 1e-9


def test_stale() -> None:
    cmd = ackermann_to_twist(0.5, 0.1, age_sec=0.3)
    assert cmd.linear_x == 0.0
    assert cmd.angular_z == 0.0
    assert cmd.reason == 'stale_command'


def test_nan() -> None:
    cmd = ackermann_to_twist(float('nan'), 0.1)
    assert cmd.linear_x == 0.0
    assert cmd.reason == 'non_finite'
