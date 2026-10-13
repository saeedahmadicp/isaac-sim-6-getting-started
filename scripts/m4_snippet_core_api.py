# Module 4.4 - "Isaac Sim Core API Workflow" snippet, rewritten for Isaac Sim 6.1.
# Paste into Window > Script Editor on an EMPTY stage (File > New From Stage Template > Empty), Ctrl+Enter, then Play.
#
# The course used omni.isaac.core (4.2):
#     from omni.isaac.core.objects import DynamicCuboid
#     from omni.isaac.core.objects.ground_plane import GroundPlane
#     from omni.isaac.core.physics_context import PhysicsContext
# In 6.1 `omni.isaac.core` is gone and `isaacsim.core.api` is deprecated. The current API is
# isaacsim.core.experimental.*: shapes are plain geometry, and you add physics by wrapping
# them in RigidPrim (rigid body) + GeomPrim (collider).
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from pxr import UsdPhysics

import omni.usd

stage = omni.usd.get_context().get_stage()
if not any(p.IsA(UsdPhysics.Scene) for p in stage.Traverse()):  # = PhysicsContext()
    UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

GroundPlane("/World/groundPlane", sizes=10)

cube = Cube("/World/cube", sizes=1.0, positions=[-0.5, -0.2, 1.0], scales=[0.5, 0.5, 0.5])
material = PreviewSurfaceMaterial("/World/Looks/cube_color")
material.set_input_values("diffuseColor", [0.2, 0.3, 0.0])
cube.apply_visual_materials(material)
RigidPrim(cube.paths)  # = "Dynamic": adds a rigid body
GeomPrim(cube.paths, apply_collision_apis=True)  # adds a collider
