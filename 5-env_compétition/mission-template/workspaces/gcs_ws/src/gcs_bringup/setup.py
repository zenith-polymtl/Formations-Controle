import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'gcs_bringup'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Zenith, équipe contrôle',
    maintainer_email='controle@zenith-polymtl.ca',
    description='Launch files du portable GCS.',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
