from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='serving_robot',
            executable='control_center',
            output='screen',
        ),
        Node(
            package='turtlebot3_gui',
            executable='turtlebot3_gui',
            output='screen',
        ),
        Node(
            package='table_order',
            executable='table_order',
            output='screen'
        ),
        Node(
            package='database',
            executable='database_server',
            output='screen'
        )
    ])