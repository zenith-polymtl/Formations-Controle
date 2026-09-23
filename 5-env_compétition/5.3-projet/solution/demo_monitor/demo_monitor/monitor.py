#!/usr/bin/env python3
"""Surveillance de la mission démo : solution du projet du document 5.3.

Le nœud `mission_monitor` regarde et ne touche à rien : il s'abonne à l'état de la mission et à
la batterie de mavros, et publie une fois par seconde un résumé JSON sur un topic externe.

Les six règles que ce fichier illustre sont dans `5.3-projet/README.md` ; la ligne qui respecte
chacune est annotée ci-dessous.
"""

import json
import math

import rclpy
from custom_interfaces.msg import MissionState
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String

from tools import topics

# Paquet tiers : topics.py ne décrit que les topics /aeac écrits par l'équipe.
MAVROS_BATTERY = '/mavros/battery'

# Règle 2 : le label vient d'un dict indexé par les constantes du message. Aucune chaîne d'état
# n'est écrite ailleurs, et aucune valeur entière n'est recopiée à la main.
LABELS = {MissionState.IDLE: 'IDLE', MissionState.GOTO: 'GOTO',
          MissionState.ACT: 'ACT', MissionState.RETURN: 'RETURN'}
UNKNOWN_LABEL = 'INCONNU'   # tant qu'aucun MissionState n'a été reçu

# Marge de réarmement du WARN batterie, en volts : la tension doit repasser franchement
# au-dessus du seuil avant qu'un second avertissement soit permis.
BATTERY_REARM_MARGIN_V = 0.3


def format_summary(state, voltage, time_in_state):
    """Le résumé publié, en JSON, sur une ligne. Aucun appel ROS : essayable dans un python3 nu.
    Une tension absente ou non finie (NaN) devient `null` : une batterie qu'on n'a pas mesurée
    n'est pas une batterie à zéro volt, et `NaN` n'est pas du JSON."""
    voltage_ok = voltage is not None and math.isfinite(float(voltage))
    return json.dumps({
        'state': LABELS.get(state, UNKNOWN_LABEL),
        'voltage': round(float(voltage), 2) if voltage_ok else None,
        'time_in_state': round(float(time_in_state), 1),
    })


class MissionMonitor(Node):
    def __init__(self):
        super().__init__('mission_monitor')
        # Le seuil vient de la section mission_monitor: de config/demo.yaml ; 14.0 est un défaut.
        self.battery_warn_v = self.declare_parameter('battery_warn_v', 14.0).value

        self.state = None            # dernière constante de MissionState reçue
        self.time_in_state = 0.0     # telle que la mission l'a publiée
        self.voltage = None          # dernière tension reçue
        self.battery_warned = False  # le WARN de batterie basse ne sort qu'une fois par passage

        self.create_subscription(MissionState, topics.DEMO_STATE, self.state_callback, 10)
        # mavros publie la batterie en BEST_EFFORT comme ses autres capteurs : sans
        # qos_profile_sensor_data, l'abonnement ne correspond pas et aucune tension n'arrive.
        self.create_subscription(BatteryState, MAVROS_BATTERY, self.battery_callback,
                                 qos_profile_sensor_data)
        # Règle 1 : le nom du topic vient de tools/topics.py, jamais d'un littéral.
        # Règle 5 : DEMO_SUMMARY est sous le préfixe EXTERNAL, donc le résumé traverse la radio
        # et le sol le voit. C'est tout ce qu'il y a à faire pour cela.
        self.summary_pub = self.create_publisher(String, topics.DEMO_SUMMARY, 10)
        # Règle 3 : un timer, jamais un time.sleep dans un callback. Les callbacks ne font que
        # retenir la dernière valeur reçue ; la publication périodique appartient au timer.
        self.timer = self.create_timer(1.0, self.tick)
        # Règle 6 : un INFO au démarrage est un événement, pas du périodique.
        self.get_logger().info(f'Surveillance de la mission démarrée : résumé sur '
                               f'{topics.DEMO_SUMMARY}, alerte sous {self.battery_warn_v:.1f} V.')

    # --- Callbacks : courts, sans publication et sans attente ---

    def state_callback(self, msg):
        if msg.state != self.state:
            # Règle 6 : une transition est un événement, donc un INFO.
            self.get_logger().info(f'État {LABELS.get(self.state, UNKNOWN_LABEL)} -> '
                                   f'{LABELS.get(msg.state, UNKNOWN_LABEL)}')
        self.state = msg.state
        # Le temps dans l'état est calculé par la mission : le moniteur le republie tel quel.
        self.time_in_state = float(msg.time_in_state)

    def battery_callback(self, msg):
        voltage = float(msg.voltage)
        # sensor_msgs/BatteryState met NaN dans les champs que l'autopilote ne mesure pas : une
        # tension non finie n'est pas une tension basse, c'est une absence de mesure.
        if not math.isfinite(voltage):
            return
        self.voltage = voltage
        if self.voltage < self.battery_warn_v:
            if not self.battery_warned:
                # Règle 6 : le passage sous le seuil est un événement, donc un WARN, une seule
                # fois. Un WARN à chaque message noierait le journal et ne dirait rien de plus.
                self.get_logger().warn(f'Batterie sous le seuil : {self.voltage:.2f} V '
                                       f'(seuil {self.battery_warn_v:.1f} V)')
                self.battery_warned = True
        elif self.voltage > self.battery_warn_v + BATTERY_REARM_MARGIN_V:
            # Réarmé seulement quand la tension remonte franchement au-dessus du seuil : une
            # batterie qui oscille autour du seuil ne doit pas produire une ligne par message.
            self.battery_warned = False

    # --- Le timer : la seule publication ---

    def tick(self):
        msg = String()
        msg.data = format_summary(self.state, self.voltage, self.time_in_state)
        self.summary_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MissionMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
