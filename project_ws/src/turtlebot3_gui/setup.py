from setuptools import find_packages, setup

package_name = 'turtlebot3_gui'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='love',
    maintainer_email='love@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot3_point = turtlebot3_gui.turtlebot3_point:main',
            'turtlebot3_move = turtlebot3_gui.turtlebot3_move:main',
            'send_goal = turtlebot3_gui.send_goal:main',
            'pub_topic = turtlebot3_gui.pub_topic:main',
            'sub_topic = turtlebot3_gui.sub_topic:main',
            'service_server = turtlebot3_gui.service_server:main',
            'service_client = turtlebot3_gui.service_client:main',
            'nav_server = turtlebot3_gui.nav_server:main',
            'nav_client = turtlebot3_gui.nav_client:main',
        ],
    },
)
