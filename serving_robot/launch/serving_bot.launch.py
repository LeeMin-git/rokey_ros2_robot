from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='serving_robot',
            executable='serving_robot',
            name='serving_robot',
            output='screen',
        ),
        Node(
            package='serving_robot',
            executable='robot',
            name='robot',
            output='screen',
        ),
    ])