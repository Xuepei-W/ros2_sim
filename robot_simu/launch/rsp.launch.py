from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command


def generate_launch_description():

    # Package name
    package_name = FindPackageShare("diff_drive_robot")

    # Default robot description if none is specified
    urdf_path = PathJoinSubstitution([package_name, "urdf", "robot.urdf.xacro"])
    
    # Launch configurations
    urdf = LaunchConfiguration('urdf')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
            'use_sim_time', default_value='True',
            description='Use sim time if true')

    declare_urdf = DeclareLaunchArgument(
            name='urdf', default_value=urdf_path,
            description='Path to the robot description file')

    # Create a robot state publisher 
    robot_state_publisher_node= Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,'robot_description': Command(['xacro ', urdf])}],
        remappings=[
            ('/tf','tf'),
            ('/tf_static','tf_static')
        ]
    )

    # Create a trajectory node
    #trajectory_node = Node(
        #package='mogi_trajectory_server',
        #executable='mogi_trajectory_server',
        #name='mogi_trajectory_server',
        #parameters=[{'reference_frame_id': 'map'}]
    #)

    # Launch!
    return LaunchDescription([
        declare_urdf,
        declare_use_sim_time,
        robot_state_publisher_node,
        #trajectory_node
    ])