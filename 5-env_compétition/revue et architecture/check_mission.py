"""Test hors ROS de haversine_m, next_state et du noeud (stubs). Hors du depot : scratchpad."""
import importlib.util
import sys
import types

MISSION = (r'C:\Users\colin\Zenith\Control-Formations\5-env_compétition'
           r'\demo_ws\src\demo_mission\demo_mission\mission.py')


def stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class MissionStateStub:
    IDLE, GOTO, ACT, RETURN = 0, 1, 2, 3

    def __init__(self):
        self.header = types.SimpleNamespace(stamp=None)
        self.state = 0
        self.time_in_state = 0.0


class GeoPoseStampedStub:
    def __init__(self):
        position = types.SimpleNamespace(latitude=0.0, longitude=0.0, altitude=0.0)
        orientation = types.SimpleNamespace(w=0.0)
        self.header = types.SimpleNamespace(stamp=None)
        self.pose = types.SimpleNamespace(position=position, orientation=orientation)


# --- Horloge et noeud factices : juste ce que mission.py utilise ---

class FakeDuration:
    def __init__(self, nanoseconds):
        self.nanoseconds = nanoseconds


class FakeTime:
    def __init__(self, seconds):
        self.seconds = seconds

    def __sub__(self, other):
        return FakeDuration(int((self.seconds - other.seconds) * 1e9))

    def to_msg(self):
        return self.seconds


class FakeNode:
    OVERRIDES = {}

    def __init__(self, name):
        self.node_name = name
        self.now_s = 0.0
        self._params = {}
        self.logs = []

    def declare_parameters(self, namespace, parameters):
        for key, default in parameters:
            self._params[key] = self.OVERRIDES.get(key, default)

    def get_parameter(self, key):
        return types.SimpleNamespace(value=self._params[key])

    def create_subscription(self, *args, **kwargs):
        return None

    def create_publisher(self, *args, **kwargs):
        return types.SimpleNamespace(publish=lambda msg: None)

    def create_timer(self, period_s, callback):
        self.timer_period_s = period_s
        return None

    def get_logger(self):
        node = self

        def record(level):
            return lambda text: node.logs.append(f'{level} {text}')

        return types.SimpleNamespace(info=record('INFO'), warn=record('WARN'))

    def get_clock(self):
        return types.SimpleNamespace(now=lambda: FakeTime(self.now_s))


stub('rclpy', init=None, spin=None, ok=lambda: False, shutdown=None)
stub('rclpy.node', Node=FakeNode)
stub('rclpy.qos', qos_profile_sensor_data=None)
stub('mavros_msgs')
stub('mavros_msgs.msg', RCIn=object, State=object)
stub('sensor_msgs')
stub('sensor_msgs.msg', NavSatFix=object)
stub('geographic_msgs')
stub('geographic_msgs.msg', GeoPoseStamped=GeoPoseStampedStub)
stub('custom_interfaces')
stub('custom_interfaces.msg', MissionState=MissionStateStub)
stub('tools', topics=stub('tools.topics', DEMO_STATE='/aeac/external/demo/state'))

spec = importlib.util.spec_from_file_location('mission', MISSION)
mission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mission)

S = MissionStateStub
P = {'arrival_radius_m': 3.0, 'act_duration_s': 5.0}
SITE = {'home.lat': -35.363262, 'home.lon': 149.165237, 'home.alt': 584.0,
        'target.lat': -35.362800, 'target.lon': 149.165700, 'sim': True}

failures = []


def check(label, got, expected):
    ok = got == expected if not isinstance(expected, float) else abs(got - expected) < 2.0
    print(f'{"OK  " if ok else "FAIL"} {label}: attendu {expected}, obtenu {got}')
    if not ok:
        failures.append(label)


def step(state, **kwargs):
    base = dict(go=False, armed=True, guided=True, dist_target_m=None,
                dist_home_m=None, elapsed_s=0.0, params=P)
    base.update(kwargs)
    return mission.next_state(state, **base)


def build_node(overrides=None):
    FakeNode.OVERRIDES = dict(SITE, **(overrides or {}))
    node = mission.DemoMission()
    node.armed, node.guided = True, True
    return node


def rc(node, pwm):
    node.rc_callback(types.SimpleNamespace(channels=[1500] * 7 + [pwm, 1500]))


def fix(node, lat, lon, at_s=None):
    node.now_s = node.now_s if at_s is None else at_s
    node.position_callback(types.SimpleNamespace(latitude=lat, longitude=lon))


# --- Sequence complete IDLE -> GOTO -> ACT -> RETURN -> IDLE (next_state pur) ---
check('IDLE -> GOTO (GO, arme, GUIDED)', step(S.IDLE, go=True), S.GOTO)
check('GOTO : encore loin', step(S.GOTO, dist_target_m=40.0), None)
check('GOTO -> ACT (arrive)', step(S.GOTO, dist_target_m=2.0), S.ACT)
check('ACT : action en cours', step(S.ACT, elapsed_s=2.0), None)
check('ACT -> RETURN (5 s ecoulees)', step(S.ACT, elapsed_s=5.0), S.RETURN)
check('RETURN : encore loin', step(S.RETURN, dist_home_m=30.0), None)
check('RETURN -> IDLE (revenu)', step(S.RETURN, dist_home_m=1.0), S.IDLE)

# --- Refus du GO hors des conditions de securite ---
check('GO sans GUIDED', step(S.IDLE, go=True, guided=False), None)
check('GO sans armement', step(S.IDLE, go=True, armed=False), None)
check('pas de GO', step(S.IDLE, go=False), None)
check('GOTO sans position (None)', step(S.GOTO, dist_target_m=None), None)

# --- I3 : le pilote reprend la main (desarme ou sort de GUIDED) ---
check('I3 GOTO desarme -> IDLE', step(S.GOTO, armed=False, dist_target_m=40.0), S.IDLE)
check('I3 GOTO hors GUIDED -> IDLE', step(S.GOTO, guided=False, dist_target_m=40.0), S.IDLE)
check('I3 ACT desarme -> IDLE', step(S.ACT, armed=False, elapsed_s=1.0), S.IDLE)
check('I3 RETURN desarme -> IDLE', step(S.RETURN, armed=False, dist_home_m=50.0), S.IDLE)
check('I3 IDLE desarme : rien', step(S.IDLE, armed=False, guided=False), None)

node = build_node()
node.state, node.armed = S.GOTO, False
node.logs.clear()
node.tick()
check('I3 noeud : retour IDLE', node.state, S.IDLE)
check('I3 noeud : WARN pilote',
      any('Le pilote a repris la main, mission interrompue' in line for line in node.logs), True)

# --- I2 : le GO doit avoir ete relache avant de compter ---
node = build_node()
rc(node, 1900)
check('I2 interrupteur deja haut au demarrage : pas de GO', node.go, False)
rc(node, 1100)
rc(node, 1900)
check('I2 relache puis haut : GO', node.go, True)

node._transition(S.GOTO)                      # on quitte IDLE : le GO redevient a relacher
rc(node, 1900)                                # interrupteur reste haut pendant tout le vol
node.state = S.RETURN
node.logs.clear()
node._transition(S.IDLE)                      # RETURN -> IDLE, « Mission terminee »
rc(node, 1900)
check('I2 reste haut apres RETURN -> IDLE : pas de relance', node.go, False)
check('I2 mission terminee loguee',
      any('Mission terminée' in line for line in node.logs), True)
rc(node, 1100)
rc(node, 1900)
check('I2 relance possible seulement apres relachement', node.go, True)

# --- I2 bis : interrupteur bas puis haut pendant le vol, puis fin de mission ---
node = build_node()
rc(node, 1100)
rc(node, 1900)
node._transition(S.GOTO)                      # IDLE -> GOTO
rc(node, 1100)                                # le pilote rebaisse l'interrupteur en vol
rc(node, 1900)                                # ... puis le remonte
check('I2bis GO remonte en vol : go vrai avant la fin', node.go, True)
node.state = S.RETURN
node._transition(S.IDLE)                      # RETURN -> IDLE
check('I2bis retour en IDLE oublie le GO', node.go, False)
rc(node, 1900)
check('I2bis interrupteur toujours haut : pas de relance', node.go, False)
rc(node, 1100)
rc(node, 1900)
check('I2bis relachement puis GO : relance', node.go, True)

# --- M-1 : canal negatif refuse ---
node = build_node({'rc.go_channel': -1})
try:
    node.rc_callback(types.SimpleNamespace(channels=[1900, 1900]))
    check('M-1 canal negatif : pas de GO', node.go, False)
except Exception as error:
    check('M-1 canal negatif : pas de GO', repr(error), 'False')

node = build_node()
node.rc_callback(types.SimpleNamespace(channels=[1500, 1500]))
check('M7 canal hors borne : pas de GO', node.go, False)

# --- M5 : position perimee (plus de 2 s) ---
node = build_node()
fix(node, SITE['target.lat'], SITE['target.lon'], at_s=10.0)
check('M5 position fraiche : distance calculee', round(node.distance_to(node.target), 1), 0.0)
node.now_s = 11.5
check('M5 position de 1.5 s : encore valable',
      round(node.distance_to(node.target), 1), 0.0)
node.now_s = 13.0
check('M5 position de 3 s : None', node.distance_to(node.target), None)
node.state, node.go = S.GOTO, False
node.tick()
check('M5 pas d arrivee avec une position perimee', node.state, S.GOTO)

# --- C1 : coordonnees de site absentes ---
try:
    build_node({'home.lat': 0.0, 'home.lon': 0.0})
    check('C1 home absent : RuntimeError', 'aucune exception', 'RuntimeError')
except RuntimeError as error:
    check('C1 home absent : RuntimeError', str(error),
          'Coordonnées de site absentes : vérifier config/sites/<site>.yaml')
try:
    build_node({'target.lat': 0.0, 'target.lon': 0.0})
    check('C1 target absent : RuntimeError', 'aucune exception', 'RuntimeError')
except RuntimeError as error:
    check('C1 target absent : RuntimeError', str(error),
          'Coordonnées de site absentes : vérifier config/sites/<site>.yaml')

try:
    build_node({'home.lat': 0.0})
    check('C1 demi-coordonnee absente : RuntimeError', 'aucune exception', 'RuntimeError')
except RuntimeError:
    check('C1 demi-coordonnee absente : RuntimeError', 'RuntimeError', 'RuntimeError')

# --- M6 : state_rate_hz absurde, periode bornee ---
check('M6 state_rate_hz = 0 : periode bornee a 10 s',
      build_node({'state_rate_hz': 0.0}).timer_period_s, 10.0)

# --- Distance Canberra (config/sites/sim.yaml) : home -> target ---
distance = mission.haversine_m(-35.363262, 149.165237, -35.362800, 149.165700)
check('haversine home->target (m)', round(distance, 1), 65.0)
check('haversine point identique', mission.haversine_m(45.5, -73.6, 45.5, -73.6), 0)

print('LABELS =', mission.LABELS)
print('DEMO_STATE utilise =', mission.topics.DEMO_STATE)
print('RESULTAT :', 'tout passe' if not failures else f'echecs {failures}')
sys.exit(1 if failures else 0)
