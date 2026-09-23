from setuptools import find_packages, setup

package_name = 'demo_mission'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Colin Cormier',
    maintainer_email='colinc131@gmail.com',
    description='Demo mission node for Zenith training 5: a four state machine over mavros',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mission = demo_mission.mission:main',
        ],
    },
)
