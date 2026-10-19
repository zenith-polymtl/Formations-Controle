"""Mission démo de la formation 5 : le squelette d'une mission de compétition, en quatre états.

IDLE (attente du GO sur la manette), GOTO (vol vers le waypoint du site), ACT (l'action de la
mission), RETURN (retour au départ), puis IDLE. La node n'arme jamais et ne change jamais de
mode : c'est le pilote qui arme et qui met en GUIDED. Cette machine à états et la forme de son
message d'état sont un exemple pédagogique : une mission choisit les siens comme elle veut.
Trois questions auxquelles ce fichier doit répondre :
  1. Où sont les noms de topics ? Ceux de l'équipe dans tools/topics.py, ceux de mavros dessous.
  2. Où sont les états ? Dans custom_interfaces/msg/MissionState.msg, jamais redéfinis ici.
  3. Où est le waypoint ? Dans config/sites/<site>.yaml, en mètres depuis le home de l'autopilote.
"""

import math

import rclpy
from custom_interfaces.msg import MissionState
from mavros_msgs.msg import GlobalPositionTarget, HomePosition, RCIn, State
from mavros_msgs.srv import MessageInterval
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import NavSatFix

from tools import topics

# Topics de mavros. Ils appartiennent à un package tiers : topics.py ne décrit que les topics
# /aeac écrits par l'équipe, dont le deuxième segment décide de ce qui traverse la radio.
MAVROS_STATE = '/mavros/state'
MAVROS_RC_IN = '/mavros/rc/in'
MAVROS_HOME = '/mavros/home_position/home'
MAVROS_GLOBAL_POSITION = '/mavros/global_position/global'
MAVROS_SETPOINT_GLOBAL = '/mavros/setpoint_raw/global'
MAVROS_SET_MESSAGE_INTERVAL = '/mavros/set_message_interval'
GLOBAL_POSITION_INT = 33   # le message MAVLink derrière /mavros/global_position/global
HOME_POSITION = 242        # le message MAVLink derrière /mavros/home_position/home
# Une consigne de position seule : vitesse, accélération et cap ignorés (formation 3.4).
POSITION_ONLY = (GlobalPositionTarget.IGNORE_VX | GlobalPositionTarget.IGNORE_VY |
                 GlobalPositionTarget.IGNORE_VZ | GlobalPositionTarget.IGNORE_AFX |
                 GlobalPositionTarget.IGNORE_AFY | GlobalPositionTarget.IGNORE_AFZ |
                 GlobalPositionTarget.IGNORE_YAW | GlobalPositionTarget.IGNORE_YAW_RATE)

EARTH_RADIUS_M = 6371000.0
POSITION_MAX_AGE_S = 2.0   # au-delà, la position ne prouve plus où le drone se trouve
LABELS = {MissionState.IDLE: 'IDLE', MissionState.GOTO: 'GOTO',
          MissionState.ACT: 'ACT', MissionState.RETURN: 'RETURN'}

# Nom et défaut de chaque paramètre ; les vraies valeurs viennent de config/. Une valeur par
# défaut sûre est une valeur qui ne vole pas : une cible à (0, 0) du home n'en est pas une.
PARAMETERS = [
    ('sim', False), ('rc.go_channel', 7), ('rc.go_pwm_min', 1700),
    ('arrival_radius_m', 3.0), ('act_duration_s', 5.0), ('state_rate_hz', 2.0),
    ('target.north_m', 0.0), ('target.east_m', 0.0), ('altitude_agl', 10.0),
]


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance au sol entre deux points en degrés décimaux, en mètres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((phi2 - phi1) / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def offset_point(lat, lon, north_m, east_m):
    """Le point à north_m mètres au nord et east_m mètres à l'est de (lat, lon), en degrés
    décimaux. Assez juste sur quelques centaines de mètres, la taille d'un terrain de vol."""
    return (lat + math.degrees(north_m / EARTH_RADIUS_M),
            lon + math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(lat)))))


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
        self.offset = (float(values['target.north_m']), float(values['target.east_m']))
        if self.offset == (0.0, 0.0):
            raise RuntimeError('Cible de site absente : vérifier config/sites/<site>.yaml')
        self.altitude_agl = float(values['altitude_agl'])
        self.home, self.target = None, None   # (lat, lon), connus au premier home reçu
        self.state = MissionState.IDLE
        self.entered_at = self.get_clock().now()
        self.armed, self.guided, self.go = False, False, False
        self.go_released = False        # le GO doit d'abord être vu en position basse
        self.position, self.position_at = None, None   # dernier (lat, lon) reçu et son heure
        self.warned_not_ready = False   # le WARN « GO sans GUIDED » ne sort qu'une fois

        self.create_subscription(State, MAVROS_STATE, self.state_callback, 10)
        self.create_subscription(RCIn, MAVROS_RC_IN, self.rc_callback, 10)
        # Le home est celui de l'autopilote, là où il a armé : la cible se place par rapport à
        # lui, donc la mission marche où que le drone (ou le SITL) démarre.
        self.create_subscription(HomePosition, MAVROS_HOME, self.home_callback, 10)
        # Les capteurs de mavros publient en BEST_EFFORT : sans qos_profile_sensor_data,
        # l'abonnement ne correspond pas à la publication et aucune position n'arrive.
        self.create_subscription(NavSatFix, MAVROS_GLOBAL_POSITION, self.position_callback,
                                 qos_profile_sensor_data)
        # ArduPilot n'envoie sur la liaison de mavros que les messages demandés (formation 3.3,
        # section 3) : la node demande sa position et le home elle-même, et redemande tant qu'ils
        # manquent.
        self.interval_client = self.create_client(MessageInterval, MAVROS_SET_MESSAGE_INTERVAL)
        self.create_timer(1.0, self.request_messages)
        self.state_pub = self.create_publisher(MissionState, topics.DEMO_STATE, 10)
        self.setpoint_pub = self.create_publisher(GlobalPositionTarget, MAVROS_SETPOINT_GLOBAL, 10)
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

    def home_callback(self, msg):
        self.home = (msg.geo.latitude, msg.geo.longitude)
        self.target = offset_point(*self.home, *self.offset)

    def position_callback(self, msg):
        self.position = (msg.latitude, msg.longitude)
        self.position_at = self.get_clock().now()

    def request_messages(self):
        """Demande la position à 5 Hz tant qu'aucune position fraîche n'arrive, et le home tant
        qu'il manque. Une demande se perd au redémarrage de l'autopilote : ce timer la refait."""
        if not self.interval_client.service_is_ready():
            return
        if not self.position_is_fresh():
            self.interval_client.call_async(
                MessageInterval.Request(message_id=GLOBAL_POSITION_INT, message_rate=5.0))
        if self.home is None:
            self.interval_client.call_async(
                MessageInterval.Request(message_id=HOME_POSITION, message_rate=1.0))

    def tick(self):
        """Le timer : au plus une transition, puis les publications."""
        elapsed_s = (self.get_clock().now() - self.entered_at).nanoseconds / 1e9
        if self.home is None:   # tant que mavros n'a pas donné le home, il n'y a rien à viser
            self.publish_state(elapsed_s)
            return
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
            # Un setpoint de position suffirait une fois ; le republier à chaque tour rattrape
            # un message perdu. (Vitesse et accélération, elles, exigent un flux continu.)
            self.publish_setpoint(self.target if self.state == MissionState.GOTO else self.home)

    def position_is_fresh(self):
        if self.position is None:
            return False
        return (self.get_clock().now() - self.position_at).nanoseconds / 1e9 <= POSITION_MAX_AGE_S

    def distance_to(self, point):
        if not self.position_is_fresh():
            return None
        return haversine_m(*self.position, *point)

    def _transition(self, new_state):
        """Seul endroit où l'état change : il se met à jour, s'horodate et se logue."""
        self.get_logger().info(f'Transition {LABELS[self.state]} -> {LABELS[new_state]}')
        if MissionState.IDLE in (self.state, new_state):
            # Entrer ou sortir d'IDLE oublie le GO : il faudra relâcher puis remonter.
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
            # self.sim est un outil : il dit à la node qu'aucun matériel n'est branché, et le
            # launch file reste le même en simulation et en vol. Ici il n'y a qu'un endroit qui en
            # dépend ; une vraie mission les centralise (une méthode _setup_hardware() par
            # exemple) au lieu de semer des tests sur sim dans tout le fichier.
            if not self.sim:
                self._trigger_payload()
            else:
                self.get_logger().info("Simulation : l'action de la mission est sautée "
                                       '(aucun matériel branché)')

    def _trigger_payload(self):
        """L'action de la mission : larguer, photographier, ouvrir un servo. Seul appel matériel
        de la démo."""
        self.get_logger().warn('Déclenchement réel : à implémenter par la mission')

    def publish_state(self, elapsed_s):
        msg = MissionState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.state = self.state
        msg.time_in_state = float(elapsed_s)
        self.state_pub.publish(msg)

    def publish_setpoint(self, point):
        msg = GlobalPositionTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        # Altitude comptée depuis le home, comme altitude_agl : aucune conversion à faire.
        msg.coordinate_frame = GlobalPositionTarget.FRAME_GLOBAL_REL_ALT
        msg.type_mask = POSITION_ONLY
        msg.latitude, msg.longitude = point
        msg.altitude = self.altitude_agl
        self.setpoint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DemoMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
