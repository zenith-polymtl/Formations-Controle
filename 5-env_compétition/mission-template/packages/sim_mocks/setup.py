from setuptools import find_packages, setup

package_name = 'sim_mocks'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Zenith, équipe contrôle',
    maintainer_email='controle@zenith-polymtl.ca',
    description='Mocks du matériel pour la simulation, et nœuds de test qui arment.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'rc_simulator = sim_mocks.rc_simulator:main',
            'target_mock = sim_mocks.target_mock:main',
            'takeoff_test = sim_mocks.takeoff_test:main',
        ],
    },
)
