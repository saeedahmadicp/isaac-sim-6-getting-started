"""Module 4.3 checkpoint: drive Nova Carter from ROS 2 /cmd_vel with an Action Graph (Isaac Sim 6.1).

Builds the same graph as the lesson "Using OmniGraph to Drive a Robot in Isaac Sim":

    On Playback Tick ─┬─> ROS2 Subscribe Twist ──linear──> Break 3-Vector ─x─> Differential Controller ──> Articulation Controller
    ROS2 Context ─────┘                         └─angular─> Break 3-Vector ─z─┘
                                                (wheel radius 0.14, wheel distance 0.413, max 2.0 m/s / 3.0 rad/s)

Differences from the 4.5 lesson: none in the graph itself. The ROS 2 bridge auto-loads with bundled
Jazzy libraries (Ubuntu 24.04), so you do not have to source /opt/ros before launching.

Usage (from the Isaac Sim root folder):
    ./python.sh learning_resource/scripts/m4_nova_carter_cmd_vel.py
        then, in another terminal:  ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ./python.sh learning_resource/scripts/m4_nova_carter_cmd_vel.py --headless --test
        (publishes /cmd_vel itself with rclpy for 3 s and checks that the robot moved)
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless})

import omni.kit.app

ext_manager = omni.kit.app.get_app().get_extension_manager()
for ext in ["isaacsim.ros2.bridge", "isaacsim.robot.wheeled_robots.nodes", "isaacsim.core.nodes"]:
    ext_manager.set_extension_enabled_immediate(ext, True)
simulation_app.update()  # let the ROS 2 bridge finish starting before touching the stage

import omni.graph.core as og
import omni.timeline
import omni.usd
from isaacsim.storage.native import get_assets_root_path
from pxr import Gf, UsdGeom, UsdPhysics

assets_root = get_assets_root_path()
omni.usd.get_context().new_stage()
simulation_app.update()
stage = omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

# Environment + robot (GUI: Window > Browsers > Isaac Sim Assets, or Create > Environments / Create > Robots)
room = stage.DefinePrim("/World/SimpleRoom", "Xform")
room.GetReferences().AddReference(assets_root + "/Isaac/Environments/Simple_Room/simple_room.usd")
robot = stage.DefinePrim("/World/nova_carter", "Xform")
robot.GetReferences().AddReference(assets_root + "/Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd")
robot_xf = UsdGeom.Xformable(robot)  # lift slightly off the floor (the asset root may already carry xform ops)
translate_op = next((op for op in robot_xf.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeTranslate), None)
(translate_op or robot_xf.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble)).Set(Gf.Vec3d(0, 0, 0.05))
while omni.usd.get_context().get_stage_loading_status()[2] > 0:
    simulation_app.update()
simulation_app.update()

art_root = None  # the lesson's "Add Target > nova_carter > chassis_link"
for prim in stage.Traverse():
    if prim.HasAPI(UsdPhysics.ArticulationRootAPI) and str(prim.GetPath()).startswith("/World/nova_carter"):
        art_root = str(prim.GetPath())
        break
wheel_joints = [str(p.GetName()) for p in stage.Traverse() if p.IsA(UsdPhysics.RevoluteJoint) and "wheel" in p.GetName()]
print(f"[m4] articulation root: {art_root}")
print(f"[m4] wheel joints found: {wheel_joints}")

og.Controller.edit(
    {"graph_path": "/World/nova_carter_cmd_vel", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ROS2Context", "isaacsim.ros2.bridge.ROS2Context"),
            ("SubscribeTwist", "isaacsim.ros2.bridge.ROS2SubscribeTwist"),
            ("BreakLinear", "omni.graph.nodes.BreakVector3"),
            ("BreakAngular", "omni.graph.nodes.BreakVector3"),
            ("DifferentialController", "isaacsim.robot.wheeled_robots.DifferentialController"),
            ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
        ],
        og.Controller.Keys.SET_VALUES: [
            ("SubscribeTwist.inputs:topicName", "cmd_vel"),
            ("DifferentialController.inputs:wheelRadius", 0.14),
            ("DifferentialController.inputs:wheelDistance", 0.413),
            ("DifferentialController.inputs:maxLinearSpeed", 2.0),
            ("DifferentialController.inputs:maxAngularSpeed", 3.0),
            ("ArticulationController.inputs:robotPath", art_root),
            ("ArticulationController.inputs:jointNames", ["joint_wheel_left", "joint_wheel_right"]),
        ],
        og.Controller.Keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "SubscribeTwist.inputs:execIn"),
            ("ROS2Context.outputs:context", "SubscribeTwist.inputs:context"),
            ("SubscribeTwist.outputs:linearVelocity", "BreakLinear.inputs:tuple"),
            ("SubscribeTwist.outputs:angularVelocity", "BreakAngular.inputs:tuple"),
            ("SubscribeTwist.outputs:execOut", "DifferentialController.inputs:execIn"),
            ("BreakLinear.outputs:x", "DifferentialController.inputs:linearVelocity"),
            ("BreakAngular.outputs:z", "DifferentialController.inputs:angularVelocity"),
            ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
            ("DifferentialController.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
        ],
    },
)

timeline = omni.timeline.get_timeline_interface()
timeline.play()

if args.test:
    import rclpy
    from geometry_msgs.msg import Twist

    rclpy.init()
    node = rclpy.create_node("m4_test_publisher")
    pub = node.create_publisher(Twist, "cmd_vel", 10)
    msg = Twist()
    msg.linear.x = 0.5
    chassis = UsdGeom.Xformable(stage.GetPrimAtPath(art_root))
    p0 = chassis.ComputeLocalToWorldTransform(0).ExtractTranslation()
    for i in range(240):  # ~4 s
        if i > 30:
            pub.publish(msg)
        simulation_app.update()
    p1 = chassis.ComputeLocalToWorldTransform(0).ExtractTranslation()
    dist = (p1 - p0).GetLength()
    print(f"[m4] robot moved {dist:.3f} m while /cmd_vel linear.x = 0.5")
    print("[m4] PASS: Nova Carter follows /cmd_vel" if dist > 0.5 else "[m4] FAIL: robot did not follow /cmd_vel")
    node.destroy_node()
    rclpy.shutdown()
    timeline.stop()
    simulation_app.close()
else:
    print("[m4] Playing. Publish geometry_msgs/Twist on /cmd_vel (e.g. teleop_twist_keyboard).")
    while simulation_app.is_running():
        simulation_app.update()
    simulation_app.close()
