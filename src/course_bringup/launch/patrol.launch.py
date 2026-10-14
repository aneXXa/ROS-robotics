"""Система patrol в namespace: turtlesim + patrol + pose_relay + optional bag."""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    LogInfo,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='evidence/pr05/bag',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='best_effort',
        ),
        LogInfo(msg=['patrol.launch: namespace=', namespace,
                     ' record=', record,
                     ' subscriber_reliability=', subscriber_reliability]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        GroupAction([
            PushRosNamespace(namespace),
            Node(
                package='patrol',
                executable='patrol',
                name='patrol',
                output='screen',
                remappings=[('cmd_vel', '/turtle1/cmd_vel')],
            ),
            Node(
                package='course_bringup',
                executable='pose_relay',
                name='pose_relay',
                output='screen',
            ),
            Node(
                package='course_bringup',
                executable='pose_subscriber',
                name='pose_subscriber',
                output='screen',
                parameters=[{'reliability': subscriber_reliability}],
            ),
        ]),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', '/robot_a/sensor_pose',
            ],
            output='screen',
            condition=IfCondition(
                PythonExpression(["'", record, "' == 'true'"])
            ),
        ),
    ])
