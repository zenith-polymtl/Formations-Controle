"""Launch de la mission démo : un seul nœud, deux fichiers de configuration du dépôt.

`config/demo.yaml` est déjà au format paramètres ROS 2 (`demo_mission: ros__parameters:`) et se
passe tel quel au nœud. `config/sites/<site>.yaml` ne l'est pas, et on ne change pas son format
pour ne pas toucher au template : ce launch le lit lui-même avec le module `yaml`, dans une
`OpaqueFunction` parce que le nom du site n'est connu qu'au moment du lancement, et il aplatit
les clés utiles en paramètres du nœud.
"""

import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

CONFIG_DIR = '/aeac/config'   # le dépôt est toujours monté à /aeac dans les conteneurs


def site_parameters(site):
    """Aplatit config/sites/<site>.yaml en paramètres du nœud."""
    path = f'{CONFIG_DIR}/sites/{site}.yaml'
    try:
        with open(path) as handle:
            site_config = yaml.safe_load(handle)['site']
        return {
            'home.lat': float(site_config['home']['lat']),
            'home.lon': float(site_config['home']['lon']),
            'home.alt': float(site_config['home']['alt']),
            'target.lat': float(site_config['scene']['target']['lat']),
            'target.lon': float(site_config['scene']['target']['lon']),
            'altitude_agl': float(site_config['altitude_agl']),
        }
    except FileNotFoundError:
        raise RuntimeError(f'Site inconnu : {path}') from None
    except (KeyError, TypeError) as error:
        raise RuntimeError(f'{path} : clé manquante ou mal formée ({error})') from None


def launch_setup(context, *args, **kwargs):
    site = LaunchConfiguration('site').perform(context)
    return [
        Node(
            package='demo_mission',
            executable='mission',
            name='demo_mission',
            output='screen',
            parameters=[
                f'{CONFIG_DIR}/demo.yaml',
                site_parameters(site),
                {'sim': ParameterValue(LaunchConfiguration('sim'), value_type=bool)},
            ],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='false',
                              description='Vrai en simulation : aucun appel matériel'),
        DeclareLaunchArgument('site', default_value='sim',
                              description='Terrain, donc config/sites/<site>.yaml'),
        OpaqueFunction(function=launch_setup),
    ])
