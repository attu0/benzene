from setuptools import find_packages, setup

package_name = 'benzene_imu'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/imu.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='atharv',
    maintainer_email='atharvmudse@gmail.com',
    description='MPU6050 I2C IMU driver for the benzene robot',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mpu6050_publisher = benzene_imu.mpu6050_publisher:main',
        ],
    },
)