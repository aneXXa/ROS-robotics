"""Структурные проверки URDF: связность и parent lidar_link."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

URDF_XACRO = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'


def _process_xacro() -> str:
    xacro = pytest.importorskip('xacro')
    return xacro.process_file(str(URDF_XACRO)).toxml()


def test_xacro_expands() -> None:
    xml = _process_xacro()
    assert 'base_link' in xml
    assert 'lidar_link' in xml


def test_lidar_parent_is_base_link() -> None:
    root = ET.fromstring(_process_xacro())
    joint = root.find("./joint[@name='lidar_link_joint']")
    assert joint is not None
    parent = joint.find('parent')
    assert parent is not None
    assert parent.get('link') == 'base_link'


def test_sensor_frames_present() -> None:
    root = ET.fromstring(_process_xacro())
    names = {link.get('name') for link in root.findall('link')}
    assert {'base_link', 'camera_link', 'lidar_link', 'imu_link'} <= names
