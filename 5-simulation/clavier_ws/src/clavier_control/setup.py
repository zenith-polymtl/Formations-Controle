from setuptools import find_packages, setup

package_name = 'clavier_control'

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
    maintainer='Colin Rousseau',
    maintainer_email='colinc131@gmail.com',
    description='Keyboard teleop and keyboard control nodes from Zenith training 3.4, for simulation',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'teleop = clavier_control.teleop:main',
            'keyboard_control = clavier_control.keyboard_control:main',
        ],
    },
)
