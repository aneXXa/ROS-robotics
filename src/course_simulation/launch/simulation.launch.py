"""Headless Gazebo + bridge + RSP + drive/odom adapters (+ optional drive_source)."""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def _setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory('course_simulation')
    default_world = os.path.join(pkg_share, 'worlds', 'mcity-minimal.sdf')
    default_bridge = os.path.join(pkg_share, 'config', 'bridge.yaml')
    default_models = os.path.join(pkg_share, 'models')

    world = LaunchConfiguration('world').perform(context) or default_world
    bridge_config = LaunchConfiguration('bridge_config').perform(context) or default_bridge
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'
    namespace = LaunchConfiguration('namespace').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time')
    publish_cmd = LaunchConfiguration('publish_cmd')

    models_path = default_models
    existing = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    gz_resource = models_path if not existing else f'{models_path}:{existing}'

    gz_cmd = ['gz', 'sim']
    if headless:
        gz_cmd += ['-s', '-r', '--headless-rendering']
    else:
        gz_cmd += ['-r']
    gz_cmd.append(world)

    xacro_file = PathJoinSubstitution([
        FindPackageShare('course_description'),
        'urdf',
        'vehicle.urdf.xacro',
    ])
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str,
    )

    actions = [
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource),
        LogInfo(msg=[
            'simulation.launch namespace=', namespace,
            ' headless=', LaunchConfiguration('headless'),
            ' world=', world,
            ' bridge=', bridge_config,
        ]),
        ExecuteProcess(cmd=gz_cmd, output='screen', name='gazebo'),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            output='screen',
            parameters=[{
                'config_file': bridge_config,
                'use_sim_time': use_sim_time,
            }],
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
        ),
        Node(
            package='course_simulation',
            executable='drive_adapter',
            name='drive_adapter',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package='course_simulation',
            executable='odom_adapter',
            name='odom_adapter',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package='course_simulation',
            executable='drive_source',
            name='drive_source',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'speed': 0.6,
                'steering_angle': 0.1,
            }],
            condition=IfCondition(
                PythonExpression(["'", publish_cmd, "' == 'true'"])
            ),
        ),
    ]
    return actions


def generate_launch_description():
    pkg_share = get_package_share_directory('course_simulation')
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_share, 'worlds', 'mcity-minimal.sdf'),
        ),
        DeclareLaunchArgument(
            'bridge_config',
            default_value=os.path.join(pkg_share, 'config', 'bridge.yaml'),
        ),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('publish_cmd', default_value='true'),
        OpaqueFunction(function=_setup),
    ])
