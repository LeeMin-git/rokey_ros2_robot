from setuptools import find_packages, setup

package_name = 'table_order'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'PyQt5', 'table_order_interface'],  # Add necessary dependencies
    zip_safe=True,
    maintainer='psb',
    maintainer_email='soobgg773@gmail.com',
    description='A ROS 2 package for handling table orders with GUI and service interface',
    license='Apache-2.0',  # Change to the correct license
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'table_order = table_order.OrderTable:main',
            'table_order_copy = table_order.OrderTableCopy:main',
            'response_test = table_order.response_test:main'
        ],
    },
)
