from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'course_simulation'


def tree_files(src_root: str, dest_root: str):
    """Install nested model/world/config trees into share/."""
    entries = []
    for dirpath, _, filenames in os.walk(src_root):
        if not filenames:
            continue
        rel = os.path.relpath(dirpath, '.')
        entries.append((
            os.path.join('share', package_name, rel),
            [os.path.join(rel, name) for name in filenames],
        ))
    return entries


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        *tree_files('config', 'config'),
        *tree_files('models', 'models'),
        *tree_files('worlds', 'worlds'),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aneXXa',
    maintainer_email='an_na_rib@mail.ru',
    description='Gazebo simulation bringup with drive and odom adapters.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'drive_adapter = course_simulation.drive_adapter:main',
            'odom_adapter = course_simulation.odom_adapter:main',
            'drive_source = course_simulation.drive_source:main',
        ],
    },
)
