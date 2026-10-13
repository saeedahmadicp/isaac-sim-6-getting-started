"""Module 1.3/1.4 checkpoint: 2D lidar on SimpleRobot -> ROS 2 LaserScan -> RViz (Isaac Sim 6.1).

The course adds a *PhysX* rotating lidar and wires "Isaac Read Lidar Beams -> ROS2 Publish Laser Scan".
In 6.1 the PhysX lidar is deprecated (extsDeprecated/isaacsim.sensors.physx), so this uses the
replacement: an *RTX* lidar with the 2D config "Example_Rotary_2D", published through the same
graph that Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar builds.

Expected: ~10 LaserScan msgs/s on /scan_lidar, frame sim_lidar, 3600 beams, and a forward beam of
2.50 m to an obstacle placed 2.50 m ahead.

Prerequisite: learning_resource/output/simple_robot.usd (run m1_build_simple_robot.py --save ... first,
or save your own robot there).

Usage (from the Isaac Sim root folder):
    ./python.sh learning_resource/scripts/m1_ros2_lidar.py
        then: ros2 topic echo /scan_lidar --once     /    rviz2  (Fixed Frame = sim_lidar, Add > By topic > /scan_lidar)
    ./python.sh learning_resource/scripts/m1_ros2_lidar.py --headless --test
"""

import argparse
import os

HERE = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
parser.add_argument("--test", action="store_true", help="Subscribe to /scan_lidar and check the obstacle is seen")
parser.add_argument("--usd", default=os.path.join(os.path.dirname(HERE), "output", "simple_robot.usd"))
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless, "enable_motion_bvh": True})  # RTX lidar needs motion BVH

import omni.kit.app

omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("isaacsim.ros2.bridge", True)
simulation_app.update()  # let the ROS 2 bridge finish starting before touching the stage

import omni.kit.commands
import omni.timeline
import omni.usd
from isaacsim.ros2.nodes import Ros2RtxLidarGraphConfig, create_ros2_rtx_lidar_graph
from isaacsim.sensors.experimental.rtx import Lidar
from omni.physx.scripts import utils as physx_utils
from pxr import Gf, UsdGeom, UsdPhysics

omni.usd.get_context().open_stage(args.usd)
simulation_app.update()
stage = omni.usd.get_context().get_stage()

# Stop the rear-wheel drives from lesson 1.1 so the robot stands still for the scan check
for joint in ["Rear_Left_Joint", "Rear_Right_Joint"]:
    UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"/World/SimpleRobot/{joint}"), "angular").GetTargetVelocityAttr().Set(0.0)

# --- Lesson 1.3 (6.1 version): lidar on the chassis body -----------------------------------------
# The course mounts the lidar on Front_Sensor, its own rigid body fixed to the chassis with a Fixed Joint.
# On this 6.1 build an RTX lidar under such a fixed-jointed link published NOTHING (also under a
# scale-compensating Xform), while a lidar directly under the chassis body works - which is also how
# Nova Carter mounts its sensors. So: select Cube > Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D.
# Its Translate is in Cube-local units (Cube is scaled 2 x 1 x 0.5): (0.45, 0, 1.0) = 0.9 m forward and
# 0.5 m above the chassis centre, i.e. above the wheel tops so the scan doesn't hit the robot itself.
lidar = Lidar.create(
    path="/World/SimpleRobot/Cube/Lidar", config="Example_Rotary_2D", tick_rate=10.0, translations=[[0.45, 0.0, 1.0]]
)
lidar_path = lidar.paths[0]

# An obstacle whose front face is 2.5 m in front of the lidar (lesson: add cubes/cones, Rigid Body with Colliders Preset)
omni.kit.commands.execute("CreateMeshPrimWithDefaultXform", prim_type="Cube", prim_path="/World/Obstacle")
# Create > Mesh prims carry translate/orient/scale ops; set the translate op directly (XformCommonAPI
# silently refuses prims that have an orient op).
stage.GetPrimAtPath("/World/Obstacle").GetAttribute("xformOp:translate").Set(Gf.Vec3d(3.9, 0.0, 0.5))
physx_utils.setRigidBody(stage.GetPrimAtPath("/World/Obstacle"), "convexHull", False)

# --- Lesson 1.4: Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar (Laser Scan ticked) ------------
graph_path = create_ros2_rtx_lidar_graph(
    Ros2RtxLidarGraphConfig(
        graph_path="/World/ROS2_LidarStream",
        lidar_prim=lidar_path,
        frame_id="sim_lidar",
        publish_laser_scan=True,
        laser_scan_topic="scan_lidar",
    )
)
print(f"[m1] ROS 2 lidar graph: {graph_path}  lidar: {lidar_path}")

timeline = omni.timeline.get_timeline_interface()
timeline.play()

if args.test:
    import rclpy
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import LaserScan

    rclpy.init()
    node = rclpy.create_node("m1_scan_check")
    scans = []
    node.create_subscription(LaserScan, "scan_lidar", lambda m: scans.append(m), qos_profile_sensor_data)
    import time

    t0, frames = time.time(), 0
    while (len(scans) < 3 or frames < 180) and frames < 1500:  # RTX sensors can take a while to warm up on the first run
        simulation_app.update()
        rclpy.spin_once(node, timeout_sec=0.0)
        frames += 1
    print(f"[m1] waited {frames} frames / {time.time() - t0:.1f} s")
    from isaacsim.core.experimental.prims import RigidPrim

    pos, _ = RigidPrim("/World/SimpleRobot/Cube").get_world_poses()
    print(f"[m1] chassis world position: {pos.numpy()[0].round(3)}")
    if scans:
        m = scans[-1]
        valid = [r for r in m.ranges if m.range_min < r < m.range_max]
        closest = min(valid) if valid else float("nan")
        import math

        def beam(angle_deg):
            i = int(round((math.radians(angle_deg) - m.angle_min) / m.angle_increment)) % len(m.ranges)
            return m.ranges[i]

        i_min = min(range(len(m.ranges)), key=lambda i: m.ranges[i] if m.range_min < m.ranges[i] < m.range_max else 1e9)
        print(f"[m1] forward beam = {beam(0):.2f} m (obstacle face expected at 2.50 m), "
              f"closest return at {math.degrees(m.angle_min + i_min * m.angle_increment):.0f} deg")
        print(f"[m1] got {len(scans)} LaserScan msgs, frame={m.header.frame_id}, {len(m.ranges)} beams, closest={closest:.2f} m")
        ok = m.header.frame_id == "sim_lidar" and abs(beam(0) - 2.5) < 0.1 and closest > 2.0
        print("[m1] PASS: /scan_lidar sees the obstacle" if ok else "[m1] FAIL: unexpected scan")
    else:
        print(f"[m1] FAIL: no LaserScan received on /scan_lidar; topics seen: {node.get_topic_names_and_types()}")
    node.destroy_node()
    rclpy.shutdown()
    timeline.stop()
    simulation_app.close()
else:
    print("[m1] Playing. Try: ros2 topic echo /scan_lidar --once   or   rviz2 (Fixed Frame: sim_lidar)")
    while simulation_app.is_running():
        simulation_app.update()
    simulation_app.close()
