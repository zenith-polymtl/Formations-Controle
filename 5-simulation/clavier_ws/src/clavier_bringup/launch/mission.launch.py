"""Vol au clavier, formation 5.1 : la téléop et le contrôle clavier de la formation 3.4.

make sim C=clavier lance ce fichier avec sim:=true. Les deux nodes ne partent qu'en simulation :
lancé sur le drone (sim:=false), ce fichier ne démarre rien.
Le clavier est lu dans le terminal de make sim : c'est lui qui doit avoir le focus.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    sim = DeclareLaunchArgument('sim', default_value='false',
                                description='Vrai en simulation : sinon, rien ne démarre')
    only_in_sim = IfCondition(LaunchConfiguration('sim'))

    # output='screen' : l'aide de la téléop s'affiche dans le terminal
    teleop = Node(
        package='clavier_control',
        executable='teleop',
        name='teleop',
        output='screen',
        condition=only_in_sim,
    )
    keyboard_control = Node(
        package='clavier_control',
        executable='keyboard_control',
        name='keyboard_control',
        # Plus rapide que les défauts de la 3.4 (2 m/s, 1 m/s, 0,5 rad/s)
        parameters=[{'horizontal_speed': 5.0, 'vertical_speed': 2.0, 'yaw_rate': 1.0}],
        condition=only_in_sim,
    )

    ld.add_action(sim)
    ld.add_action(teleop)
    ld.add_action(keyboard_control)
    return ld
