"""Проверка ожидаемых исходных/нормализованных frames одометрии."""

from course_simulation.odom_adapter import DST_BASE, DST_ODOM, SRC_BASE, SRC_ODOM


def test_frame_contract() -> None:
    assert SRC_ODOM == 'course_ackermann/odom'
    assert SRC_BASE == 'course_ackermann/base_link'
    assert DST_ODOM == 'odom'
    assert DST_BASE == 'base_link'
