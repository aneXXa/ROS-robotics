"""Тестовый источник /drive/safe со stamp из /clock (use_sim_time)."""

from __future__ import annotations

from ackermann_msgs.msg import AckermannDriveStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy


class DriveSource(Node):
    def __init__(self) -> None:
        super().__init__('drive_source')
        self.declare_parameter('speed', 0.6)
        self.declare_parameter('steering_angle', 0.0)
        self.declare_parameter('rate_hz', 20.0)
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(AckermannDriveStamped, '/drive/safe', qos)
        hz = float(self.get_parameter('rate_hz').value)
        self.create_timer(1.0 / max(hz, 1.0), self._tick)

    def _tick(self) -> None:
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.drive.speed = float(self.get_parameter('speed').value)
        msg.drive.steering_angle = float(self.get_parameter('steering_angle').value)
        self._pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = DriveSource()
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
