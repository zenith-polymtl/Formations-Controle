#!/usr/bin/env python3
"""Nœud de test : passe en GUIDED, arme et décolle. Simulation seulement.

    ros2 run sim_mocks takeoff_test --ros-args -p sim:=true -p alt:=10.0

Refuse de démarrer si le paramètre sim n'est pas vrai. C'est la seule façon d'armer depuis le
code dans ce dépôt : un nœud de mission n'arme jamais et ne change jamais de mode, c'est le pilote
qui le fait. Ce nœud existe pour aller plus vite en simulation, comme la node takeoff de la
formation 3.4. Il n'est inclus par aucun launch.
"""

import rclpy
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from rclpy.node import Node


class TakeoffTest(Node):
    def __init__(self):
        super().__init__('takeoff_test')
        self.declare_parameter('sim', False)
        self.declare_parameter('alt', 10.0)
        if not self.get_parameter('sim').value:
            raise SystemExit('takeoff_test ne tourne qu\'en simulation : ajoute -p sim:=true')
        self.mode = self.create_client(SetMode, '/mavros/set_mode')
        self.arm = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.takeoff = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        self.step = 0
        self.pending = None
        self.timer = self.create_timer(1.0, self.tick)  # une étape par seconde, sans bloquer

    def tick(self):
        if self.pending is not None and not self.pending.done():
            return
        if self.step == 0:
            self.get_logger().info('mode GUIDED')
            self.pending = self.call(self.mode, SetMode.Request(custom_mode='GUIDED'))
        elif self.step == 1:
            self.get_logger().info('armement (renvoyé tant que refusé)')
            self.pending = self.call(self.arm, CommandBool.Request(value=True))
            if self.pending is None or (self.pending.done() and not self.pending.result().success):
                return  # on réessaie à la prochaine seconde
        elif self.step == 2:
            alt = float(self.get_parameter('alt').value)
            self.get_logger().info(f'décollage à {alt} m')
            self.pending = self.call(self.takeoff, CommandTOL.Request(altitude=alt))
        else:
            self.get_logger().info('terminé')
            raise SystemExit
        self.step += 1

    def call(self, client, request):
        if not client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn(f'{client.srv_name} absent, mavros est-il lancé ?')
            self.step -= 1
            return None
        return client.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    try:
        node = TakeoffTest()
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit) as e:
        if str(e):
            print(e)
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
