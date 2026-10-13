"""Capture real Isaac Sim frames from the lesson 1.1 checkpoint scene.

First save the checkpoint, then run this helper from the Isaac Sim installation:
    ./python.sh learning_resource/scripts/m1_build_simple_robot.py --headless --test --save learning_resource/output/simple_robot.usd
    ./python.sh learning_resource/scripts/capture_first_robot.py --stage learning_resource/output/simple_robot.usd --output-dir learning_resource/screenshots/first_robot

The camera, lighting, and display colours are for readability. Geometry, joints,
and drives are loaded unchanged. This records simulated motion, not GUI actions.
"""

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stage", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args, _ = parser.parse_known_args()
if not args.stage.is_file():
    parser.error(f"Stage does not exist: {args.stage}")
args.output_dir.mkdir(parents=True, exist_ok=True)

from isaacsim import SimulationApp

app = SimulationApp({"headless": True, "width": 1440, "height": 900,
                     "renderer": "RealTimePathTracing", "multi_gpu": False})

try:
    import carb
    import numpy as np
    import omni.replicator.core as rep
    import omni.timeline
    import omni.usd
    from PIL import Image
    from pxr import Gf, UsdGeom, UsdLux

    if not omni.usd.get_context().open_stage(str(args.stage.resolve())):
        raise RuntimeError("Could not open checkpoint stage")
    for _ in range(20):
        app.update()
    stage = omni.usd.get_context().get_stage()
    body = stage.GetPrimAtPath("/World/SimpleRobot/Cube")
    if not body.IsValid():
        raise RuntimeError("Expected the lesson 1.1 SimpleRobot checkpoint")
    xf = UsdGeom.Xformable(body)
    UsdGeom.Gprim(body).GetDisplayColorAttr().Set([Gf.Vec3f(0.12, 0.38, 0.65)])
    for prim in stage.Traverse():
        if prim.GetName().endswith("_Wheel"):
            UsdGeom.Gprim(prim).GetDisplayColorAttr().Set([Gf.Vec3f(0.16, 0.18, 0.22)])
    dome = UsdLux.DomeLight.Define(stage, "/World/CaptureDome")
    dome.GetIntensityAttr().Set(300.0)
    sun = UsdLux.DistantLight.Define(stage, "/World/defaultLight/DistantLight")
    sun.GetIntensityAttr().Set(1200.0)
    sun.GetAngleAttr().Set(2.0)
    UsdGeom.Xformable(sun).ClearXformOpOrder()
    UsdGeom.Xformable(sun).AddRotateXYZOp().Set(Gf.Vec3f(-45, 25, 0))
    settings = carb.settings.get_settings()
    settings.set("/rtx/post/tonemap/op", 4)
    settings.set("/rtx/post/tonemap/filmIso", 200.0)
    settings.set("/rtx/post/tonemap/enabled", True)
    camera = UsdGeom.Camera.Define(stage, "/World/CourseCamera")
    camera.CreateFocalLengthAttr(32.0)
    camera.CreateClippingRangeAttr(Gf.Vec2f(0.1, 100.0))
    camera_op = UsdGeom.Xformable(camera).AddTransformOp()

    def aim(eye, target, up=(0, 0, 1)):
        camera_op.Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye), Gf.Vec3d(*target), Gf.Vec3d(*up)).GetInverse())

    aim((5.5, -7.0, 4.5), (0.5, 0, 0.3))
    rep.orchestrator.set_capture_on_play(False)
    product = rep.create.render_product(str(camera.GetPath()), (1440, 900))
    rgb = rep.AnnotatorRegistry.get_annotator("rgb")
    rgb.attach([product])
    for _ in range(60):
        app.update()
    frames = []

    def capture(name):
        rep.orchestrator.step(rt_subframes=16, delta_time=0.0, pause_timeline=True)
        pixels = np.asarray(rgb.get_data())[:, :, :3]
        if pixels.shape != (900, 1440, 3) or pixels.std() < 5 or not 10 < pixels.mean() < 220:
            raise RuntimeError(f"Invalid capture: shape={pixels.shape}, mean={pixels.mean()}, std={pixels.std()}")
        Image.fromarray(pixels).save(args.output_dir / name)
        frames.append({"file": name, "mean_rgb": round(float(pixels.mean()), 2),
                       "std_rgb": round(float(pixels.std()), 2),
                       "body_position": list(xf.ComputeLocalToWorldTransform(0).ExtractTranslation())})

    timeline = omni.timeline.get_timeline_interface()
    capture("assembled.png")
    timeline.play()
    for _ in range(180):
        app.update()
    timeline.pause()
    end_time = timeline.get_current_time()
    capture("driving.png")
    x = xf.ComputeLocalToWorldTransform(0).ExtractTranslation()[0]
    if not 0.5 < x < 1.5:
        raise RuntimeError(f"Unexpected driven displacement: {x}")
    aim((x, 0, 7), (x, 0, 0), (1, 0, 0))
    capture("wheel-layout.png")
    record = {"stage": str(args.stage), "frames": frames, "updates": 180,
              "timeline_seconds": end_time, "displacement_x_m": x,
              "presentation_changes": "Camera, lights, chassis/wheel display colours only; physics unchanged."}
    (args.output_dir / "capture.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"[capture] PASS: {len(frames)} frames, displacement={x:.3f} m, timeline={end_time:.3f} s")
    rgb.detach([product])
    product.destroy()
    timeline.stop()
finally:
    app.close()
