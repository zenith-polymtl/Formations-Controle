"""Mission démo de la formation 5 : le squelette d'une mission de compétition, en quatre états.

IDLE (attente du GO sur la manette), GOTO (vol vers le waypoint du site), ACT (action factice),
RETURN (retour au départ), puis IDLE. Le nœud n'arme jamais et ne change jamais de mode : c'est
le pilote qui arme et qui met en GUIDED. Trois questions auxquelles ce fichier doit répondre :
  1. Où sont les noms de topics ? Ceux de l'équipe dans tools/topics.py, ceux de mavros dessous.
  2. Où sont les états ? Dans custom_interfaces/msg/MissionState.msg, jamais redéfinis ici.
  3. Où est le waypoint ? Dans config/sites/<site>.yaml, aplati en paramètres par le launch.
"""

import math

import rclpy
from custom_interfaces.msg import MissionState
from geographic_msgs.msg import GeoPoseStamped
from mavros_msgs.msg import RCIn, State
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import NavSatFix

from tools import topics

# Topics de mavros. Ils appartiennent à un paquet tiers : topics.py ne décrit que les topics
# /aeac écrits par l'équipe, dont le deuxième segment décide de ce qui traverse la radio.
MAVROS_STATE = '/mavros/state'
MAVROS_RC_IN = '/mavros/rc/in'
MAVROS_GLOBAL_POSITION = '/mavros/global_position/global'
MAVROS_SETPOINT_GLOBAL = '/mavros/setpoint_position/global'

EARTH_RADIUS_M = 6371000.0
POSITION_MAX_AGE_S = 2.0   # au-delà, la position ne prouve plus où le drone se trouve
LABELS = {MissionState.IDLE: 'IDLE', MissionState.GOTO: 'GOTO',
          MissionState.ACT: 'ACT', MissionState.RETURN: 'RETURN'}

# Nom et défaut de chaque paramètre ; les vraies valeurs viennent de config/. Une valeur par
# défaut sûre est une valeur qui ne vole pas : (0.0, 0.0) n'est pas un site, et il est refusé.
PARAMETERS = [
    ('sim', False), ('rc.go_channel', 7), ('rc.go_pwm_min', 1700),
    ('arrival_radius_m', 3.0), ('act_duration_s', 5.0), ('state_rate_hz', 2.0),
    ('home.lat', 0.0), ('home.lon', 0.0), ('home.alt', 0.0),
    ('target.lat', 0.0), ('target.lon', 0.0), ('altitude_agl', 10.0),
]


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance au sol entre deux points en degrés décimaux, en mètres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((phi2 - phi1) / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def next_state(state, *, go, armed, guided, dist_target_m, dist_home_m, elapsed_s, params):
    """Machine à états pure, vérifiable sans ROS : le nouvel état, ou None s'il n'y en a pas.
    Une distance vaut None tant qu'aucune position fraîche n'est reçue, donc pas d'arrivée."""
    # Hors IDLE, perdre l'armement ou le mode GUIDED veut dire que le pilote a repris la main.
    if state != MissionState.IDLE and not (armed and guided):
        return MissionState.IDLE
    if state == MissionState.IDLE and go and armed and guided:
        return MissionState.GOTO
    if state == MissionState.GOTO and dist_target_m is not None:
        if dist_target_m < params['arrival_radius_m']:
            return MissionState.ACT
    if state == MissionState.ACT and elapsed_s >= params['act_duration_s']:
        return MissionState.RETURN
    if state == MissionState.RETURN and dist_home_m is not None:
        if dist_home_m < params['arrival_radius_m']:
            return MissionState.IDLE
    return None


class DemoMission(Node):
    def __init__(self):
        super().__init__('demo_mission')
        self.declare_parameters('', PARAMETERS)
        values = {name: self.get_parameter(name).value for name, _ in PARAMETERS}
        self.sim = bool(values['sim'])   # lu une seule fois, au démarrage
        self.go_channel = int(values['rc.go_channel'])
        self.go_pwm_min = int(values['rc.go_pwm_min'])
        self.params = {'arrival_radius_m': float(values['arrival_radius_m']),
                       'act_duration_s': float(values['act_duration_s'])}
        self.home = (float(values['home.lat']), float(values['home.lon']))
        self.target = (float(values['target.lat']), float(values['target.lon']))
        if 0.0 in self.home + self.target:
            raise RuntimeError('Coordonnées de site absentes : vérifier config/sites/<site>.yaml')
        # mavros attend une altitude au-dessus de l'ellipsoïde WGS-84 alors que home.alt est en
        # AMSL : l'écart est accepté pour la démo, une vraie mission passe par un géoïde.
        self.setpoint_alt = float(values['home.alt']) + float(values['altitude_agl'])
        self.state = MissionState.IDLE
        self.entered_at = self.get_clock().now()
        self.armed, self.guided, self.go = False, False, False
        self.go_released = False        # le GO doit d'abord être vu en position basse
        self.position, self.position_at = None, None   # dernier (lat, lon) reçu et son heure
        self.warned_not_ready = False   # le WARN « GO sans GUIDED » ne sort qu'une fois

        self.create_subscription(State, MAVROS_STATE, self.state_callback, 10)
        self.create_subscription(RCIn, MAVROS_RC_IN, self.rc_callback, 10)
        # Les capteurs de mavros publient en BEST_EFFORT : sans qos_profile_sensor_data,
        # l'abonnement ne correspond pas à la publication et aucune position n'arrive.
        self.create_subscription(NavSatFix, MAVROS_GLOBAL_POSITION, self.position_callback,
                                 qos_profile_sensor_data)
        self.state_pub = self.create_publisher(MissionState, topics.DEMO_STATE, 10)
        self.setpoint_pub = self.create_publisher(GeoPoseStamped, MAVROS_SETPOINT_GLOBAL, 10)
        # Exécuteur mono-thread : timer et callbacks ne se chevauchent jamais, self.state est
        # donc sans verrou. Pas de MultiThreadedExecutor sans y penser.
        self.timer = self.create_timer(1.0 / max(0.1, float(values['state_rate_hz'])), self.tick)
        self.get_logger().info(f'Mission démo prête en {LABELS[self.state]} : GO attendu sur le '
                               f'canal {self.go_channel + 1} de la manette.')

    def state_callback(self, msg):
        self.armed, self.guided = msg.armed, msg.mode == 'GUIDED'

    def rc_callback(self, msg):
        if 0 <= self.go_channel < len(msg.channels):
            high = msg.channels[self.go_channel] >= self.go_pwm_min
            if not high:
                self.go_released = True
            self.go = high and self.go_released
        else:
            self.go = False   # canal absent du message : pas de GO

    def position_callback(self, msg):
        self.position = (msg.latitude, msg.longitude)
        self.position_at = self.get_clock().now()

    def tick(self):
        """Le timer : au plus une transition, puis les publications."""
        elapsed_s = (self.get_clock().now() - self.entered_at).nanoseconds / 1e9
        new_state = next_state(self.state, go=self.go, armed=self.armed, guided=self.guided,
                               dist_target_m=self.distance_to(self.target),
                               dist_home_m=self.distance_to(self.home),
                               elapsed_s=elapsed_s, params=self.params)
        if new_state is not None:
            self._transition(new_state)
            elapsed_s = 0.0
        elif self.state == MissionState.IDLE and self.go and not self.warned_not_ready:
            self.get_logger().warn("GO reçu mais le drone n'est pas armé en GUIDED")
            self.warned_not_ready = True
        self.publish_state(elapsed_s)
        if self.state in (MissionState.GOTO, MissionState.RETURN):
            # mavros exige un flux continu de setpoints, sinon l'autopilote les ignore.
            self.publish_setpoint(self.target if self.state == MissionState.GOTO else self.home)

    def distance_to(self, point):
        if self.position is None:
            return None
        if (self.get_clock().now() - self.position_at).nanoseconds / 1e9 > POSITION_MAX_AGE_S:
            return None
        return haversine_m(self.position[0], self.position[1], point[0], point[1])

    def _transition(self, new_state):
        """Seul endroit où l'état change : il se met à jour, s'horodate et se logue."""
        self.get_logger().info(f'Transition {LABELS[self.state]} -> {LABELS[new_state]}')
        if MissionState.IDLE in (self.state, new_state):
            # Entrer ou sortir d'IDLE oublie le GO : il faudra relâcher puis remonter
            # l'interrupteur pour la mission suivante.
            self.go, self.go_released = False, False
        self.state = new_state
        self.entered_at = self.get_clock().now()
        self.warned_not_ready = False
        if new_state == MissionState.IDLE:
            if self.armed and self.guided:
                self.get_logger().info('Mission terminée')
            else:
                self.get_logger().warn('Le pilote a repris la main, mission interrompue')
        elif new_state == MissionState.ACT:
            # L'unique appel matériel de la démo, et donc le seul endroit entouré d'un test sur
            # le paramètre sim : le launch reste le même en simulation et en vol.
            if not self.sim:
                self._trigger_payload()
            else:
                self.get_logger().info("Simulation : action factice, rien n'est déclenché")

    def _trigger_payload(self):
        self.get_logger().warn('Déclenchement réel : à implémenter par la mission')

    def publish_state(self, elapsed_s):
        msg = MissionState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.state = self.state
        msg.time_in_state = float(elapsed_s)
        self.state_pub.publish(msg)

    def publish_setpoint(self, point):
        msg = GeoPoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.latitude, msg.pose.position.longitude = point
        msg.pose.position.altitude = self.setpoint_alt
        msg.pose.orientation.w = 1.0
        self.setpoint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DemoMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
