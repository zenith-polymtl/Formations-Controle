import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'clavier_bringup'

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
    maintainer='Colin Rousseau',
    maintainer_email='colinc131@gmail.com',
    description='Launch file of the keyboard flight for Zenith training 5',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
