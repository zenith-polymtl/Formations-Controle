#!/usr/bin/env python3
"""Surveillance de la mission démo : squelette du projet du document 5.3.

Les imports, la classe, le paramètre, les subscribers, le publisher et le timer sont en place ;
les six `# TODO n :` sont à écrire. Le cahier des charges, les six règles et la liste complète
des fichiers à toucher sont dans `5.3-projet/README.md`, à lire avant d'écrire une ligne.

Tel quel, ce squelette se construit, mais il ne démarre qu'avec DEMO_SUMMARY dans topics.py
(5.3, section 2.4) ; il crée alors son topic, et n'y publie rien avant le TODO 6.
"""

import json

import rclpy
from custom_interfaces.msg import MissionState
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String

from tools import topics

# Package tiers : topics.py ne décrit que les topics /aeac écrits par l'équipe.
MAVROS_BATTERY = '/mavros/battery'

LABELS = {MissionState.IDLE: 'IDLE', MissionState.GOTO: 'GOTO',
          MissionState.ACT: 'ACT', MissionState.RETURN: 'RETURN'}
UNKNOWN_LABEL = 'INCONNU'   # tant qu'aucun MissionState n'a été reçu


def format_summary(state, voltage, time_in_state):
    """Le résumé publié, en JSON, sur une ligne. Aucun appel ROS : se vérifie seule dans python3.

    Exemple de sortie attendue :
        {"state": "GOTO", "voltage": 15.8, "time_in_state": 12.4}
    """
    # TODO 1 : construire le dictionnaire des trois champs et le rendre en JSON avec json.dumps.
    #   - le label d'état se lit dans LABELS, jamais écrit à la main (UNKNOWN_LABEL par défaut) ;
    #   - une tension pas encore reçue (None) reste absente : null en JSON, pas 0.0 ;
    #   - arrondir la tension au centième et le temps au dixième, sinon le résumé est illisible.
    return '{}'


class MissionMonitor(Node):
    def __init__(self):
        super().__init__('mission_monitor')
        # Le seuil vient de la section mission_monitor: de config/demo.yaml ; 14.0 est un défaut.
        self.battery_warn_v = self.declare_parameter('battery_warn_v', 14.0).value

        self.state = None            # dernière constante de MissionState reçue
        self.time_in_state = 0.0     # telle que la mission l'a publiée
        self.voltage = None          # dernière tension reçue
        self.battery_warned = False  # le WARN de batterie basse ne sort qu'une fois

        self.create_subscription(MissionState, topics.DEMO_STATE, self.state_callback, 10)
        # mavros publie la batterie en BEST_EFFORT comme ses autres capteurs : sans
        # qos_profile_sensor_data, la subscription ne correspond pas et aucune tension n'arrive.
        self.create_subscription(BatteryState, MAVROS_BATTERY, self.battery_callback,
                                 qos_profile_sensor_data)
        # Le nom du topic vient de tools/topics.py, et le préfixe EXTERNAL suffit à le faire
        # traverser la radio : c'est la ligne à ajouter dans topics.py (voir le README).
        self.summary_pub = self.create_publisher(String, topics.DEMO_SUMMARY, 10)
        # Un timer, jamais un time.sleep dans un callback.
        self.timer = self.create_timer(1.0, self.tick)
        self.get_logger().info(f'Surveillance de la mission démarrée : résumé sur '
                               f'{topics.DEMO_SUMMARY}, alerte sous {self.battery_warn_v:.1f} V.')

    # --- Callbacks : courts, sans publication et sans attente ---

    def state_callback(self, msg):
        # TODO 2 : si l'état reçu diffère de celui retenu, loguer la transition en INFO
        #   (les labels viennent de LABELS, jamais écrits à la main ; l'état se compare à une
        #   constante de MissionState, jamais à 'IDLE' ni à 0).
        # TODO 3 : retenir l'état reçu et le temps dans l'état publié par la mission, qui se
        #   republie tel quel : c'est la mission qui le calcule, pas le moniteur.
        pass

    def battery_callback(self, msg):
        # TODO 4 : retenir la tension reçue (msg.voltage, en volts).
        # TODO 5 : sous self.battery_warn_v, un WARN et un seul (self.battery_warned sert à
        #   cela). Aucun log si la tension est normale : le journal ne reçoit que des événements.
        pass

    # --- Le timer : la seule publication ---

    def tick(self):
        # TODO 6 : remplir un std_msgs/String avec format_summary(...) et le publier sur
        #   self.summary_pub. Rien d'autre ne publie dans cette node.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = MissionMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
