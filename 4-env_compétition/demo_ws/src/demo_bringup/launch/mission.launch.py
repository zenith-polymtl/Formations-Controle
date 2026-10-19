"""Launch file de la mission démo : une node, deux fichiers de configuration du repo.

`config/demo.yaml` et `config/sites/<site>.yaml` sont tous deux au format paramètres ROS 2 :
ils se passent tels quels à la node, sans lecture YAML ici. Les clés imbriquées du site
(`target: {north_m: ...}`) arrivent à la node sous les noms `target.north_m`, `target.east_m`
et `altitude_agl`.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

CONFIG_DIR = '/aeac/config'   # le repo est toujours monté à /aeac dans les conteneurs


def generate_launch_description():
    ld = LaunchDescription()

    sim = DeclareLaunchArgument('sim', default_value='false',
                                description='Vrai en simulation : aucun appel matériel')
    site = DeclareLaunchArgument('site', default_value='sim',
                                 description='Terrain, donc config/sites/<site>.yaml')
    mission = Node(
        package='demo_mission',
        executable='mission',
        name='demo_mission',
        output='screen',
        parameters=[
            f'{CONFIG_DIR}/demo.yaml',
            PathJoinSubstitution([f'{CONFIG_DIR}/sites',
                                  [LaunchConfiguration('site'), '.yaml']]),
            {'sim': ParameterValue(LaunchConfiguration('sim'), value_type=bool)},
        ],
    )

    ld.add_action(sim)
    ld.add_action(site)
    ld.add_action(mission)
    return ld
