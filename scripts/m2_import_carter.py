"""Module 2 checkpoint: import the Carter URDF and drive it with a Differential Controller (Isaac Sim 6.1).

Reproduces lessons 2.1 + 2.2 of "Ingesting Robot Assets and Simulating Your Robot in Isaac Sim"
with the 6.1 URDF importer:

1. Convert learning_resource/assets/carter/urdf/carter.urdf -> learning_resource/output/carter/carter.usda
   (Base Type = Mobile, like the course's "moveable base").
2. New stage + Flat Grid environment (falls back to a plain ground plane if the asset server is offline).
3. Reference the robot at /World/carter, select the "physx" Physics variant (new in 6.x).
4. Configure drives (the 6.1 importer dialog no longer has a "Joints and Drives" section):
   left_wheel / right_wheel -> velocity drive (stiffness 0, damping 10000)
   rear_pivot / rear_axle   -> passive (stiffness 0, damping 0)
5. Build the same Action Graph that Tools > Robotics > OmniGraph Controllers > Differential Controller makes
   (without keyboard nodes): OnPlaybackTick -> DifferentialController -> ArticulationController.

Usage (from the Isaac Sim root folder):
    ./python.sh learning_resource/scripts/m2_import_carter.py
    ./python.sh learning_resource/scripts/m2_import_carter.py --headless --test
"""

import argparse
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
parser.add_argument("--test", action="store_true", help="Drive forward ~3 s, check motion, then exit")
parser.add_argument("--linear", type=float, default=0.2, help="Desired linear velocity (m/s)")
parser.add_argument("--angular", type=float, default=0.0, help="Desired angular velocity (rad/s)")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless})

import omni.kit.app

ext_manager = omni.kit.app.get_app().get_extension_manager()
for ext in ["omni.scene.optimizer.core", "isaacsim.robot.schema", "isaacsim.robot.wheeled_robots.nodes"]:
    ext_manager.set_extension_enabled_immediate(ext, True)

import omni.graph.core as og
import omni.kit.commands
import omni.timeline
import omni.usd
from isaacsim.asset.importer.urdf.impl import URDFImporter, URDFImporterConfig
from isaacsim.storage.native import get_assets_root_path
from pxr import Gf, UsdGeom, UsdPhysics

# --- 1. URDF -> USD --------------------------------------------------------------------------
# The Carter URDF ships with Isaac Sim; copy it next to the course files on first use (lesson 2.1).
carter_dir = os.path.join(ROOT, "assets", "carter")
if not os.path.isfile(os.path.join(carter_dir, "urdf", "carter.urdf")):
    import shutil

    src = os.path.join(os.path.dirname(ROOT), "exts", "isaacsim.asset.importer.urdf", "data", "urdf", "robots", "carter")
    shutil.copytree(src, carter_dir, dirs_exist_ok=True)
    print(f"[m2] copied Carter URDF from {src}")
config = URDFImporterConfig(
    urdf_path=os.path.join(carter_dir, "urdf", "carter.urdf"),
    usd_path=os.path.join(ROOT, "output"),
    fix_base=False,  # GUI: Options > Base Type = Mobile
)
carter_usd = URDFImporter(config).import_urdf()
print(f"[m2] converted URDF -> {carter_usd}")

# --- 2. Scene ----------------------------------------------------------------------------------
omni.usd.get_context().new_stage()
simulation_app.update()
stage = omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

assets_root = get_assets_root_path()
if assets_root:  # Create > Environments > Flat Grid
    grid = stage.DefinePrim("/World/FlatGrid", "Xform")
    grid.GetReferences().AddReference(assets_root + "/Isaac/Environments/Grid/default_environment.usd")
    print(f"[m2] Flat Grid from {assets_root}")
else:
    omni.kit.commands.execute(
        "AddGroundPlaneCommand", stage=stage, planePath="/World/GroundPlane", axis="Z",
        size=25.0, position=Gf.Vec3f(0.0), color=Gf.Vec3f(0.5),
    )
    print("[m2] asset server unreachable -> plain ground plane")

# --- 3. Reference the robot + pick the physics variant ----------------------------------------
robot = stage.DefinePrim("/World/carter", "Xform")
robot.GetReferences().AddReference(carter_usd)
robot.GetVariantSet("Physics").SetVariantSelection("physx")  # Property > Variants > Physics
robot_xf = UsdGeom.Xformable(robot)  # lift slightly off the floor (the asset root may already carry xform ops)
translate_op = next((op for op in robot_xf.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeTranslate), None)
(translate_op or robot_xf.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble)).Set(Gf.Vec3d(0, 0, 0.05))
simulation_app.update()

# --- 4. Drives ---------------------------------------------------------------------------------
for name, damping in [("left_wheel", 10000.0), ("right_wheel", 10000.0), ("rear_pivot", 0.0), ("rear_axle", 0.0)]:
    drive = UsdPhysics.DriveAPI.Apply(stage.GetPrimAtPath(f"/World/carter/Physics/{name}"), "angular")
    drive.CreateStiffnessAttr().Set(0.0)
    drive.CreateDampingAttr().Set(damping)

# --- 5. Differential controller graph ---------------------------------------------------------
# Wheel radius 0.24 m (collision cylinder), wheel distance 2 x 0.3142 m (joint localPos0 Y offset).
og.Controller.edit(
    {"graph_path": "/World/Graphs/differential_controller", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("DifferentialController", "isaacsim.robot.wheeled_robots.DifferentialController"),
            ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
        ],
        og.Controller.Keys.SET_VALUES: [
            ("DifferentialController.inputs:wheelRadius", 0.24),
            ("DifferentialController.inputs:wheelDistance", 0.6284),
            ("DifferentialController.inputs:maxLinearSpeed", 0.5),
            ("DifferentialController.inputs:maxAngularSpeed", 1.0),
            ("DifferentialController.inputs:linearVelocity", args.linear),
            ("DifferentialController.inputs:angularVelocity", args.angular),
            ("ArticulationController.inputs:robotPath", "/World/carter"),
            ("ArticulationController.inputs:jointNames", ["left_wheel", "right_wheel"]),
        ],
        og.Controller.Keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "DifferentialController.inputs:execIn"),
            ("OnPlaybackTick.outputs:deltaSeconds", "DifferentialController.inputs:dt"),
            ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
            ("DifferentialController.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
        ],
    },
)

# --- Run ---------------------------------------------------------------------------------------
timeline = omni.timeline.get_timeline_interface()
timeline.play()
chassis = UsdGeom.Xformable(stage.GetPrimAtPath("/World/carter/Geometry/chassis_link"))
if args.test:
    for _ in range(180):
        simulation_app.update()
    pos = chassis.ComputeLocalToWorldTransform(0).ExtractTranslation()
    print(f"[m2] chassis position after 3 s = ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
    timeline.stop()
    print("[m2] PASS: Carter drove forward" if pos[0] > 0.2 else "[m2] FAIL: Carter did not drive forward")
    simulation_app.close()
else:
    while simulation_app.is_running():
        simulation_app.update()
    simulation_app.close()
