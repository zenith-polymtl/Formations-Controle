from setuptools import find_packages, setup

package_name = 'demo_monitor'

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
    description='Mission monitor for Zenith training 5: publishes a JSON summary of the demo mission',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'monitor = demo_monitor.monitor:main',
        ],
    },
)
