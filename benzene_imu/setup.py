#!/usr/bin/env python3

"""
*****************************************************************************************
*
*                           =========================
*                              benzene_imu
*                           =========================
*
*  Python package setup for the Benzene MPU6050 IMU driver.
*
*****************************************************************************************
"""

from setuptools import find_packages
from setuptools import setup


PACKAGE_NAME = 'benzene_imu'


setup(
    name=PACKAGE_NAME,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + PACKAGE_NAME],
        ),
        (
            'share/' + PACKAGE_NAME,
            ['package.xml'],
        ),
        (
            'share/' + PACKAGE_NAME + '/launch',
            ['launch/imu.launch.py'],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='atharv',
    maintainer_email='atharvmudse@gmail.com',
    description='MPU6050 I2C IMU driver for the Benzene robot',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mpu6050_publisher = benzene_imu.mpu6050_publisher:main',
        ],
    },
)