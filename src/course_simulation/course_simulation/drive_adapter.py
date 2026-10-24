"""Адаптер /drive/safe → /vehicle/gz_cmd_vel."""

from __future__ import annotations

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from rclpy.time import Time

from course_simulation.drive_logic import ackermann_to_twist


class DriveAdapter(Node):
    def __init__(self) -> None:
        super().__init__('drive_adapter')
        self.declare_parameter('use_sim_time', True)
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(Twist, '/vehicle/gz_cmd_vel', qos)
        self.create_subscription(
            AckermannDriveStamped,
            '/drive/safe',
            self._on_cmd,
            qos,
        )

    def _on_cmd(self, msg: AckermannDriveStamped) -> None:
        now = self.get_clock().now()
        stamp = Time.from_msg(msg.header.stamp)
        age = (now - stamp).nanoseconds * 1e-9
        result = ackermann_to_twist(
            msg.drive.speed,
            msg.drive.steering_angle,
            age_sec=age,
        )
        if result.reason:
            self.get_logger().warn(
                f'reject command: {result.reason}',
                throttle_duration_sec=1.0,
            )
        out = Twist()
        out.linear.x = result.linear_x
        out.angular.z = result.angular_z
        self._pub.publish(out)


def main() -> None:
    rclpy.init()
    node = DriveAdapter()
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
