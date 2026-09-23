#!/usr/bin/env python3
"""Simule une détection : publie la position d'une cible fixe, comme le ferait le conteneur vision.

    ros2 run sim_mocks target_mock --ros-args -p topic:=/aeac/internal/vision/target -p x:=5.0 -p y:=3.0

Le message est un geometry_msgs/PointStamped dans le repère local (mètres, ENU). Si la mission
attend un autre type de message, on écrit un mock à côté de celui-ci, on ne le complique pas.
"""

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node


class TargetMock(Node):
    def __init__(self):
        super().__init__('target_mock')
        self.declare_parameter('topic', '/aeac/internal/vision/target')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('x', 5.0)
        self.declare_parameter('y', 5.0)
        self.declare_parameter('z', 0.0)
        self.declare_parameter('rate_hz', 2.0)
        topic = self.get_parameter('topic').value
        self.pub = self.create_publisher(PointStamped, topic, 10)
        self.timer = self.create_timer(1.0 / self.get_parameter('rate_hz').value, self.publish)
        self.get_logger().info(f'Cible simulée sur {topic}')

    def publish(self):
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        msg.point.x = float(self.get_parameter('x').value)
        msg.point.y = float(self.get_parameter('y').value)
        msg.point.z = float(self.get_parameter('z').value)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TargetMock()
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
