"""Run a Script Editor snippet as a standalone app (and optionally self-check it).

The snippets m4_snippet_*.py are meant for Window > Script Editor. This runner lets you run the same
code from a terminal, which is the "standalone Python" workflow the course does not cover:

    ./python.sh learning_resource/scripts/m4_run_snippet.py learning_resource/scripts/m4_snippet_core_api.py
    ./python.sh learning_resource/scripts/m4_run_snippet.py learning_resource/scripts/m4_snippet_usd_api.py --headless --test
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("snippet")
parser.add_argument("--headless", action="store_true")
parser.add_argument("--test", action="store_true", help="Play 2 s and check that a cube fell onto the ground")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": args.headless})

import omni.timeline
import omni.usd
from pxr import UsdGeom, UsdPhysics

omni.usd.get_context().new_stage()
simulation_app.update()
with open(args.snippet) as f:
    exec(compile(f.read(), args.snippet, "exec"), {"__name__": "__snippet__"})
simulation_app.update()

stage = omni.usd.get_context().get_stage()
cube = next(p for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI))
z0 = UsdGeom.Xformable(cube).ComputeLocalToWorldTransform(0).ExtractTranslation()[2]
timeline = omni.timeline.get_timeline_interface()
timeline.play()
if args.test:
    for _ in range(120):
        simulation_app.update()
    z1 = UsdGeom.Xformable(cube).ComputeLocalToWorldTransform(0).ExtractTranslation()[2]
    print(f"[m4] {cube.GetPath()} z: {z0:.3f} -> {z1:.3f}")
    print("[m4] PASS: cube fell and rests on the ground" if 0.1 < z1 < z0 - 0.3 else "[m4] FAIL")
    timeline.stop()
    simulation_app.close()
else:
    while simulation_app.is_running():
        simulation_app.update()
    simulation_app.close()
