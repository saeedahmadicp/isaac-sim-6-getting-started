"""Module 1 checkpoint: build the course's 4-wheeled "SimpleRobot" in Isaac Sim 6.1.

This reproduces lessons 1.1 and 1.2 of "Building Your First Robot in Isaac Sim" using the
same Kit commands the GUI menus call, so the result matches what you build by hand:

- Physics Scene + Ground Plane
- SimpleRobot (Xform) > Cube chassis (2 x 1 x 0.5 m) + 4 cylinder wheels (diameter 0.75 m)
- Rigid Body with Colliders Preset on chassis and wheels
- 4 revolute joints (axis Y, Local Rotation 1 = -90, 0, 0)
- Angular drives on the rear joints (damping 10000, target velocity 50 deg/s)
- Articulation Root on SimpleRobot (needed by the Differential Controller in lesson 1.2)

Usage (from the Isaac Sim root folder):
    ./python.sh learning_resource/scripts/m1_build_simple_robot.py            # GUI, keeps running
    ./python.sh learning_resource/scripts/m1_build_simple_robot.py --headless --test
    ./python.sh learning_resource/scripts/m1_build_simple_robot.py --save learning_resource/output/simple_robot.usd
"""

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", help="Run without a window")
parser.add_argument("--test", action="store_true", help="Simulate ~3 s, check the robot drove forward, then exit")
parser.add_argument("--save", default=None, help="Save the built stage to this .usd path")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless})

import omni.kit.commands
import omni.timeline
import omni.usd
from omni.physx.scripts import utils as physx_utils
from pxr import Gf, PhysxSchema, UsdGeom, UsdPhysics

omni.usd.get_context().new_stage()
simulation_app.update()
stage = omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)


def set_xform(path, translate=(0, 0, 0), rotate_xyz=(0, 0, 0), scale=(1, 1, 1)):
    """Set Translate / Orient / Scale, the same ops the Property > Transform panel edits.

    Rotation is given in XYZ euler degrees (what the panel shows) and stored as a quaternion.
    """
    prim = stage.GetPrimAtPath(path)
    xf = UsdGeom.Xformable(prim)
    xf.ClearXformOpOrder()
    rot = (
        Gf.Rotation(Gf.Vec3d(1, 0, 0), rotate_xyz[0])
        * Gf.Rotation(Gf.Vec3d(0, 1, 0), rotate_xyz[1])
        * Gf.Rotation(Gf.Vec3d(0, 0, 1), rotate_xyz[2])
    )
    xf.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble).Set(Gf.Vec3d(*translate))
    xf.AddOrientOp(UsdGeom.XformOp.PrecisionDouble).Set(Gf.Quatd(rot.GetQuat()))
    xf.AddScaleOp(UsdGeom.XformOp.PrecisionDouble).Set(Gf.Vec3d(*scale))


def create_mesh(prim_type, path):
    """Same as Create > Mesh > <prim_type>."""
    omni.kit.commands.execute("CreateMeshPrimWithDefaultXform", prim_type=prim_type, prim_path=path)
    return stage.GetPrimAtPath(path)


# --- Lesson 1.1 Part 2: physics scene + ground plane --------------------------------------------
UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")  # Create > Physics > Physics Scene
omni.kit.commands.execute(  # Create > Physics > Ground Plane
    "AddGroundPlaneCommand",
    stage=stage,
    planePath="/World/GroundPlane",
    axis="Z",
    size=25.0,
    position=Gf.Vec3f(0.0),
    color=Gf.Vec3f(0.5),
)
UsdGeom.Xform.Define(stage, "/World/defaultLight")
omni.kit.commands.execute("CreatePrim", prim_type="DistantLight", prim_path="/World/defaultLight/DistantLight")

# --- Lesson 1.1 Part 3: chassis + hierarchy -----------------------------------------------------
WHEEL_RADIUS = 0.375  # cylinder mesh is 1 m tall / 1 m diameter -> scale 0.75 gives 0.75 m diameter
UsdGeom.Xform.Define(stage, "/World/SimpleRobot")
set_xform("/World/SimpleRobot", translate=(0, 0, WHEEL_RADIUS))  # wheels rest on the ground
chassis = create_mesh("Cube", "/World/SimpleRobot/Cube")
set_xform(chassis.GetPath(), scale=(2, 1, 0.5))

# --- Lesson 1.1 Part 4: wheels ------------------------------------------------------------------
wheels = {
    "Front_Left_Wheel": (0.5, 0.75, 0),
    "Front_Right_Wheel": (0.5, -0.75, 0),
    "Rear_Left_Wheel": (-0.5, 0.75, 0),
    "Rear_Right_Wheel": (-0.5, -0.75, 0),
}
for name, pos in wheels.items():
    create_mesh("Cylinder", f"/World/SimpleRobot/{name}")
    set_xform(f"/World/SimpleRobot/{name}", translate=pos, rotate_xyz=(90, 0, 0), scale=(0.75, 0.75, 0.25))

# Right-click > Add > Physics > Rigid Body with Colliders Preset
for path in ["/World/SimpleRobot/Cube"] + [f"/World/SimpleRobot/{n}" for n in wheels]:
    physx_utils.setRigidBody(stage.GetPrimAtPath(path), "convexHull", False)

# --- Lesson 1.1 Part 5: revolute joints (select Cube first, then the wheel) ---------------------
local_rot1 = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90).GetQuat()  # Local Rotation 1 = (-90, 0, 0)
joints = {}
for name in wheels:
    joint_name = name.replace("_Wheel", "_Joint")
    joint = physx_utils.createJoint(stage, "Revolute", chassis, stage.GetPrimAtPath(f"/World/SimpleRobot/{name}"))
    new_path = f"/World/SimpleRobot/{joint_name}"
    omni.kit.commands.execute("MovePrim", path_from=str(joint.GetPath()), path_to=new_path)
    joint = UsdPhysics.RevoluteJoint.Get(stage, new_path)
    joint.GetAxisAttr().Set("Y")
    joint.GetLocalRot0Attr().Set(Gf.Quatf(1, 0, 0, 0))
    joint.GetLocalRot1Attr().Set(Gf.Quatf(local_rot1))
    joints[joint_name] = joint.GetPrim()

# --- Lesson 1.1 Part 6: angular drive on the rear wheels ----------------------------------------
for joint_name in ["Rear_Left_Joint", "Rear_Right_Joint"]:
    drive = UsdPhysics.DriveAPI.Apply(joints[joint_name], "angular")  # Add > Physics > Angular Drive
    drive.CreateDampingAttr(10000.0)
    drive.CreateStiffnessAttr(0.0)
    drive.CreateTargetVelocityAttr(50.0)  # deg/s

# --- Lesson 1.2 Part 1: articulation root (required by the Differential Controller) -------------
robot_prim = stage.GetPrimAtPath("/World/SimpleRobot")
UsdPhysics.ArticulationRootAPI.Apply(robot_prim)
PhysxSchema.PhysxArticulationAPI.Apply(robot_prim)

if args.save:
    os.makedirs(os.path.dirname(os.path.abspath(args.save)), exist_ok=True)
    omni.usd.get_context().save_as_stage(os.path.abspath(args.save))
    print(f"[m1] saved stage to {os.path.abspath(args.save)}")

# --- Run ----------------------------------------------------------------------------------------
timeline = omni.timeline.get_timeline_interface()
timeline.play()

stage = omni.usd.get_context().get_stage()  # re-fetch: save_as_stage can swap the stage handle
chassis_xf = UsdGeom.Xformable(stage.GetPrimAtPath("/World/SimpleRobot/Cube"))
if args.test:
    for _ in range(180):  # ~3 s at 60 Hz
        simulation_app.update()
    x = chassis_xf.ComputeLocalToWorldTransform(0).ExtractTranslation()[0]
    print(f"[m1] chassis x after 3 s = {x:.3f} m")
    timeline.stop()
    print("[m1] PASS: robot drove forward" if x > 0.1 else "[m1] FAIL: robot did not drive forward")
    simulation_app.close()
else:
    while simulation_app.is_running():
        simulation_app.update()
    simulation_app.close()
