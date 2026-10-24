"""Нормализация /vehicle/odom_gz → /vehicle/odom + tf odom→base_link."""

from __future__ import annotations

import math

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from tf2_ros import TransformBroadcaster


SRC_ODOM = 'course_ackermann/odom'
SRC_BASE = 'course_ackermann/base_link'
DST_ODOM = 'odom'
DST_BASE = 'base_link'


def _finite_pose(msg: Odometry) -> bool:
    p = msg.pose.pose.position
    o = msg.pose.pose.orientation
    t = msg.twist.twist
    vals = [
        p.x, p.y, p.z,
        o.x, o.y, o.z, o.w,
        t.linear.x, t.linear.y, t.linear.z,
        t.angular.x, t.angular.y, t.angular.z,
    ]
    return all(math.isfinite(v) for v in vals)


class OdomAdapter(Node):
    def __init__(self) -> None:
        super().__init__('odom_adapter')
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=50,
        )
        self._pub = self.create_publisher(Odometry, '/vehicle/odom', qos)
        self._tf = TransformBroadcaster(self)
        self.create_subscription(Odometry, '/vehicle/odom_gz', self._on_odom, qos)

    def _on_odom(self, msg: Odometry) -> None:
        if msg.header.frame_id != SRC_ODOM or msg.child_frame_id != SRC_BASE:
            self.get_logger().warn(
                f'reject frames {msg.header.frame_id!r}/{msg.child_frame_id!r}',
                throttle_duration_sec=2.0,
            )
            return
        if not _finite_pose(msg):
            self.get_logger().warn('reject non-finite odometry', throttle_duration_sec=2.0)
            return

        out = Odometry()
        out.header = msg.header
        out.header.frame_id = DST_ODOM
        out.child_frame_id = DST_BASE
        out.pose = msg.pose
        out.twist = msg.twist
        self._pub.publish(out)

        tf = TransformStamped()
        tf.header = out.header
        tf.child_frame_id = DST_BASE
        tf.transform.translation.x = out.pose.pose.position.x
        tf.transform.translation.y = out.pose.pose.position.y
        tf.transform.translation.z = out.pose.pose.position.z
        tf.transform.rotation = out.pose.pose.orientation
        self._tf.sendTransform(tf)


def main() -> None:
    rclpy.init()
    node = OdomAdapter()
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
