#!/usr/bin/env python3
"""Simule la manette : les touches du clavier deviennent des valeurs PWM sur /mavros/rc/in.

À lancer en avant-plan dans un terminal qui a le focus (il lit le clavier) :
    ros2 run sim_mocks rc_simulator

Touches (canal 8, 9 et 10 de la manette, numérotés 7, 8, 9 dans le message) :
    w / s / x : canal 8 haut / centre / bas
    e / d / c : canal 9 haut / centre / bas
    r / f / v : canal 10 haut / centre / bas
    q         : quitter
Les autres canaux restent à 1500. Repris d'aeac-2026, inchangé sur le fond.
"""

import select
import sys
import termios
import threading
import tty

import rclpy
from mavros_msgs.msg import RCIn
from rclpy.node import Node

PWM_LOW, PWM_CENTER, PWM_HIGH = 1100, 1500, 1900
KEYS = {
    'w': (7, PWM_HIGH), 's': (7, PWM_CENTER), 'x': (7, PWM_LOW),
    'e': (8, PWM_HIGH), 'd': (8, PWM_CENTER), 'c': (8, PWM_LOW),
    'r': (9, PWM_HIGH), 'f': (9, PWM_CENTER), 'v': (9, PWM_LOW),
}


class RcSimulator(Node):
    def __init__(self):
        super().__init__('rc_simulator')
        self.pub = self.create_publisher(RCIn, '/mavros/rc/in', 10)
        self.channels = [PWM_CENTER] * 16
        self.timer = self.create_timer(0.1, self.publish)  # 10 Hz, comme un vrai récepteur
        self.settings = termios.tcgetattr(sys.stdin)
        self.stop = threading.Event()
        threading.Thread(target=self.keyboard_loop, daemon=True).start()
        self.get_logger().info('Manette simulée : w/s/x e/d/c r/f/v, q pour quitter')

    def keyboard_loop(self):
        while rclpy.ok() and not self.stop.is_set():
            key = self.read_key()
            if key == 'q':
                self.stop.set()
            elif key in KEYS:
                channel, pwm = KEYS[key]
                self.channels[channel] = pwm
                self.get_logger().info(f'canal {channel + 1} = {pwm}')

    def read_key(self):
        tty.setraw(sys.stdin.fileno())
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if ready else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish(self):
        if self.stop.is_set():
            raise KeyboardInterrupt
        msg = RCIn()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.channels = self.channels
        msg.rssi = 255
        self.pub.publish(msg)

    def destroy_node(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RcSimulator()
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
