from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mission_control',
            executable='drone_nour',   # mission/colin_drone_node.py : main()
            name='drone_nour',
            output='screen',
            parameters=[{'kp' : 0.5,}]
        ),
        Node(
            package='mission_control',
            executable='balloon',         # mission_control/ballon_pub.py : main()
            name='ballon',
            output='screen',
        ),
        Node(
            package='mission_control',
            executable='monitor',            # mission_control/monitor.py : main()
            name='monitor',
            output='screen',
        ),
    ])