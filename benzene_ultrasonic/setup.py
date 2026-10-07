from glob import glob
from setuptools import find_packages, setup

package_name = 'benzene_ultrasonic'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='atharv',
    maintainer_email='you@example.com',
    description='HC-SR04 ultrasonic driver and simulation relay for benzene',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'hcsr04 = benzene_ultrasonic.hcsr04_node:main',
            'scan_to_range = benzene_ultrasonic.scan_to_range_node:main',
        ],
    },
)