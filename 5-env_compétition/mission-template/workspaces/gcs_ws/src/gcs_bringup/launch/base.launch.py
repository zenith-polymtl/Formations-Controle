"""Ce que le portable GCS lance quelle que soit la mission : le heartbeat vers le drone.

`make gcs C=base` lance ce fichier seul. Le launch sol d'une mission (launch/<mission>.launch.py)
l'inclut puis ajoute ses propres nœuds :

    from launch.actions import IncludeLaunchDescription
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from ament_index_python.packages import get_package_share_directory
    base = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        get_package_share_directory('gcs_bringup') + '/launch/base.launch.py'))
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tools',
            executable='gcs_heartbeat',
            name='gcs_heartbeat',
            output='screen',
        ),
    ])
