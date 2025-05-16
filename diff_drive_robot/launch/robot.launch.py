import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction

def generate_launch_description():

    # Package name
    package_name='diff_drive_robot'

    # Launch configurations
    world = LaunchConfiguration('world')
    rviz = LaunchConfiguration('rviz')
    use_sim_time =LaunchConfiguration('use_sim_time')
    
    # Path to default world 
    world_path = os.path.join(get_package_share_directory(package_name),'worlds', 'home.world')

    # Launch Arguments
    declare_world = DeclareLaunchArgument(
        name='world', default_value=world_path,
        description='Full path to the world model file to load')
    
    declare_rviz = DeclareLaunchArgument(
        name='rviz', default_value='false',
        description='Opens rviz is set to True')
    
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time', default_value='True',
        description='Opens rviz is set to True')
    
    declare_x = DeclareLaunchArgument('x',default_value='2.5',
        description='x coordinate of robot')
    
    declare_y = DeclareLaunchArgument('y',default_value='1.5',
        description='y coordinate of robot')
    
    declare_yaw = DeclareLaunchArgument('yaw',default_value='-1.5707',
        description='yaw angle of robot')

    # Launch Robot State Publisher Node
    urdf_path = os.path.join(get_package_share_directory(package_name),'urdf','robot.urdf.xacro')
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'urdf': urdf_path}.items()
    )

    # Launch the gazebo server to initialize the simulation
    gazebo_server = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([os.path.join(
                        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
                    )]), launch_arguments={'gz_args': ['-r -s -v1 ', world], 'on_exit_shutdown': 'true'}.items()
    )

    # Always launch the gazebo client to visualize the simulation
    gazebo_client = IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([os.path.join(
                        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
                    )]), launch_arguments={'gz_args': '-g '}.items()
    )

    # Run the spawner node from the gazebo_ros package. 
    spawn_diff_bot = Node(
                        package='ros_gz_sim', 
                        executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-name', 'diff_bot',
                                   '-x', LaunchConfiguration('x'),
                                   '-y', LaunchConfiguration('y'),
                                   '-z', "0.2",
                                   '-Y', LaunchConfiguration('yaw')],
                        output='screen',
                        parameters=[
                            {'use_sim_time': LaunchConfiguration('use_sim_time')},
                        ]
    )

    # Launch the Gazebo-ROS bridge
    bridge_params = os.path.join(get_package_share_directory(package_name),'config','gz_bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',]
    )
    
    # Launch Rviz with diff bot rviz file
    rviz_config_file = os.path.join(get_package_share_directory(package_name), 'rviz', 'bot.rviz')
    rviz2 = GroupAction(
        condition=IfCondition(rviz),
        actions=[Node(
                    package='rviz2',
                    executable='rviz2',
                    arguments=['-d', rviz_config_file],
                    output='screen',)]
    )

    ekf_node = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                os.path.join(get_package_share_directory(package_name), 'config', 'ekf.yaml'),
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
                ]
        )

    # Launch them all!
    return LaunchDescription([
        # Declare launch arguments
        declare_rviz,
        declare_world,
        declare_x,
        declare_y,
        declare_yaw,

        # Launch the nodes
        rviz2,
        rsp,
        gazebo_server,
        gazebo_client,
        ros_gz_bridge,
        spawn_diff_bot,
        ekf_node
    ])