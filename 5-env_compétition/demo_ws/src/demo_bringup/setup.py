import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'demo_bringup'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Colin Cormier',
    maintainer_email='colinc131@gmail.com',
    description='Launch file and configuration samples for the Zenith training 5 demo mission',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
