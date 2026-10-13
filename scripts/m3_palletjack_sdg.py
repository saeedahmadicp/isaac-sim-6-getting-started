# Ported from NVIDIA-AI-IOT/synthetic_data_generation_training_workflow (palletjack_sdg/standalone_palletjack_sdg.py)
# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
# Modifications for Isaac Sim 6.1 (functional Replicator API, label handling) are described below.
"""Module 3: pallet-jack synthetic dataset with Replicator, ported to Isaac Sim 6.1.

Port of the course's `standalone_palletjack_sdg.py`
(github.com/NVIDIA-AI-IOT/synthetic_data_generation_training_workflow). Same scene, same
randomizations, same KITTI output. What changed for 6.1:

    omni.isaac.kit.SimulationApp                 -> isaacsim.SimulationApp
    omni.isaac.core.utils.nucleus                -> isaacsim.storage.native
    renderer "RayTracedLighting"                 -> "RealTimePathTracing" (6.x default)
    graph randomizers inside rep.trigger.on_frame()  -> rep.functional.* calls in a Python loop, followed by
      + rep.orchestrator.run()                        rep.orchestrator.step() (the 6.1 SDG examples' pattern)
    pxr.Semantics "update_semantics()"           -> block the referenced semantic attributes (RemoveProperty can't
                                                   delete them), then keep only "palletjack" rows in the KITTI files

Why not keep the graph randomizers? On this 6.1 build, (a) `rep.create.material_omnipbr` + `rep.randomizer.materials`
inside the trigger hung for >10 min, and (b) graph randomizers fired only on the first `rep.orchestrator.step()`.
The functional API has neither problem and is what the 6.1 examples use
(standalone_examples/replicator/sdg_ur10_palletizing.py, .../isaacsim.replicator.examples/randomizing_textures.py).

Usage (from the Isaac Sim root folder):
    ./python.sh learning_resource/scripts/m3_palletjack_sdg.py --num_frames 20
    ./python.sh learning_resource/scripts/m3_palletjack_sdg.py --headless --num_frames 2000 --distractors warehouse
    ./python.sh learning_resource/scripts/m3_palletjack_sdg.py --headless --test     # 5 frames + output check
Output: learning_resource/output/palletjack_data/<distractors>/Camera/{rgb,object_detection,...}
"""

import argparse
import os

HERE = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser("Dataset generator")
parser.add_argument("--headless", action="store_true")
parser.add_argument("--height", type=int, default=544)
parser.add_argument("--width", type=int, default=960)
parser.add_argument("--num_frames", type=int, default=20)
parser.add_argument("--distractors", default="warehouse", choices=["warehouse", "None"])
parser.add_argument("--data_dir", default=None)
parser.add_argument("--rt_subframes", type=int, default=4, help="Increase if moving objects leave ghosts")
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()
if args.test:
    args.num_frames = 5
# Replicator resolves relative paths under its own output root, while the checks
# below use the process working directory. Give both the same absolute path.
data_dir = os.path.abspath(args.data_dir or os.path.join(os.path.dirname(HERE), "output", "palletjack_data", args.distractors))

from isaacsim import SimulationApp

simulation_app = SimulationApp(
    {"headless": args.headless, "renderer": "RealTimePathTracing", "width": args.width, "height": args.height}
)

import numpy as np
import omni.replicator.core as rep
import omni.usd
from isaacsim.core.experimental.utils import semantics as semantics_utils
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdGeom, UsdLux

ENV_URL = "/Isaac/Environments/Simple_Warehouse/warehouse.usd"
SIMREADY = "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/DigitalTwin/Assets/Warehouse/Equipment"
PALLETJACKS = [
    f"{SIMREADY}/Pallet_Trucks/Scale_A/PalletTruckScale_A01_PR_NVD_01.usd",
    f"{SIMREADY}/Pallet_Trucks/Heavy_Duty_A/HeavyDutyPalletTruck_A01_PR_NVD_01.usd",
    f"{SIMREADY}/Pallet_Trucks/Low_Profile_A/LowProfilePalletTruck_A01_PR_NVD_01.usd",
]
DISTRACTORS_WAREHOUSE = [
    "/Isaac/Environments/Simple_Warehouse/Props/" + name
    for name in [
        "S_TrafficCone.usd", "S_WetFloorSign.usd", "SM_BarelPlastic_A_01.usd", "SM_BarelPlastic_B_01.usd",
        "SM_BottlePlasticA_02.usd", "SM_BucketPlastic_B.usd", "SM_CardBoxB_01_1262.usd", "SM_CardBoxD_01_1454.usd",
        "SM_CratePlastic_A_04.usd", "SM_CratePlastic_B_03.usd", "SM_PushcartA_02.usd", "SM_RackPile_04.usd",
    ]
]
TEXTURES = [
    "/Isaac/Materials/Textures/Patterns/" + name
    for name in [
        "nv_asphalt_yellow_weathered.jpg", "nv_tile_hexagonal_green_white.jpg", "nv_rubber_woven_charcoal.jpg",
        "nv_granite_tile.jpg", "nv_marble.jpg", "nv_brick_reclaimed.jpg", "nv_concrete_aged_with_lines.jpg",
        "nv_wooden_wall.jpg", "nv_stone_painted_grey.jpg", "nv_carpet_abstract_pattern.jpg",
    ]
]

assets_root = get_assets_root_path()
if not assets_root:
    raise SystemExit("Isaac Sim asset server not reachable; check your network / asset root setting")
gen = np.random.default_rng(args.seed)

# --- Scene -------------------------------------------------------------------------------------
print(f"[m3] loading {assets_root + ENV_URL}")
omni.usd.get_context().open_stage(assets_root + ENV_URL)
for _ in range(100):  # let the stage finish loading
    simulation_app.update()
while omni.usd.get_context().get_stage_loading_status()[2] > 0:
    simulation_app.update()
stage = omni.usd.get_context().get_stage()
rep.orchestrator.set_capture_on_play(False)

# Pallet jacks (2 of each) and distractors, under one scope
rep.functional.create.scope(name="SDG")
palletjacks = [
    rep.functional.create.reference(
        usd_path=url, parent="/SDG", name=f"palletjack_{i}_{k}"
    )
    for i, url in enumerate(PALLETJACKS)
    for k in range(2)
]
distractors = []
if args.distractors == "warehouse":
    distractors = [
        rep.functional.create.reference(usd_path=assets_root + d, parent="/SDG", name=f"distractor_{i}")
        for i, d in enumerate(DISTRACTORS_WAREHOUSE)
    ]
cam = rep.functional.create.camera(parent="/SDG", name="Camera", clipping_range=(0.1, 1000000))
textures = [assets_root + t for t in TEXTURES]
for _ in range(10):
    simulation_app.update()
while omni.usd.get_context().get_stage_loading_status()[2] > 0:
    simulation_app.update()

# The course's update_semantics(): only pallet jacks may carry labels.
# The warehouse and props use legacy "SemanticsAPI:*" labels that come from *referenced* layers, and
# prim.RemoveProperty() cannot delete those. So we block their values (USD's way to "delete" a referenced
# opinion), drop the schema, remove any new-style UsdSemantics labels, and only then label the pallet jacks.
n_stripped = 0
for prim in stage.Traverse():
    semantics_utils.remove_all_labels(prim)
    legacy = [sch for sch in prim.GetAppliedSchemas() if sch.startswith("SemanticsAPI:")]
    for sch in legacy:
        prim.RemoveAppliedSchema(sch)
    for attr in prim.GetAttributes():
        if attr.GetName().startswith("semantic:"):
            attr.Block()
    n_stripped += bool(legacy)
for prim in palletjacks:
    rep.functional.modify.semantics(prim, {"class": "palletjack"}, mode="add")
print(f"[m3] stripped labels from {n_stripped} prims, labelled {len(palletjacks)} pallet jacks")

# Materials we randomize: one OmniPBR for the floor meshes, one for the walls, one per pallet-jack steer axle
surfaces = {"SM_Floor": [], "SM_Wall": []}
steer_axles = []
for prim in stage.Traverse():
    name = prim.GetName()
    for key in surfaces:
        if key in name and prim.IsA(UsdGeom.Mesh):
            surfaces[key].append(prim)
    if "SteerAxles" in name and str(prim.GetPath()).startswith("/SDG/"):
        steer_axles.append(prim)
rect_lights = [p for p in stage.Traverse() if p.IsA(UsdLux.RectLight)]

surface_mats = dict(zip(surfaces, rep.functional.create_batch.material(mdl="OmniPBR.mdl", count=2, parent="/SDG")))
for key, prims in surfaces.items():
    for prim in prims:
        rep.functional.modify.material(prim, surface_mats[key])
axle_mats = []
if steer_axles:
    axle_mats = rep.functional.create_batch.material(mdl="OmniPBR.mdl", count=len(steer_axles), parent="/SDG")
    for prim, mat in zip(steer_axles, axle_mats):
        rep.functional.modify.material(prim, mat)
print(
    f"[m3] floor meshes: {len(surfaces['SM_Floor'])}, wall meshes: {len(surfaces['SM_Wall'])}, "
    f"steer axles: {len(steer_axles)}, rect lights: {len(rect_lights)}"
)


def randomize():
    """One frame of the course's domain randomization."""
    # Camera somewhere in the warehouse, looking at its centre
    rep.functional.modify.pose(
        cam, position_value=tuple(gen.uniform((-9.2, -11.8, 0.4), (7.2, 15.8, 4))), look_at_value=(0, 0, 0)
    )
    # Pallet jack body colour
    for mat in axle_mats:
        rep.functional.modify.attribute(mat, "inputs:diffuse_color_constant", tuple(gen.uniform(0, 1, 3)))
    # Pallet jack poses (the SimReady assets are authored in cm -> scale 0.01)
    for prim in palletjacks:
        rep.functional.modify.pose(
            prim,
            position_value=tuple(gen.uniform((-6, -6, 0), (6, 12, 0))),
            rotation_value=(0, 0, float(gen.uniform(0, 360))),
            scale_value=0.01,
        )
    for prim in distractors:
        rep.functional.modify.pose(
            prim,
            position_value=tuple(gen.uniform((-6, -6, 0), (6, 12, 0))),
            rotation_value=(0, 0, float(gen.uniform(0, 360))),
            scale_value=float(gen.uniform(1, 1.5)),
        )
    # Lights: random colour, intensity ~ N(1e5, 6e5) clipped at 0, on 1 time in 7
    for light in rect_lights:
        rep.functional.modify.attribute(light, "inputs:color", tuple(gen.uniform(0, 1, 3)))
        rep.functional.modify.attribute(light, "inputs:intensity", max(0.0, float(gen.normal(100000.0, 600000.0))))
        rep.functional.modify.visibility(light, bool(gen.integers(0, 7) == 0))
    # Floor / wall textures
    for mat in surface_mats.values():
        rep.functional.modify.attribute(mat, "inputs:diffuse_texture", str(gen.choice(textures)))
        rep.functional.modify.attribute(mat, "inputs:reflection_roughness_constant", float(gen.uniform(0, 1)))
        rep.functional.modify.attribute(mat, "inputs:metallic_constant", float(gen.choice([0, 1])))
        rep.functional.modify.attribute(mat, "inputs:enable_emission", True)
        rep.functional.modify.attribute(mat, "inputs:emissive_color_texture", str(gen.choice(textures)))
        rep.functional.modify.attribute(mat, "inputs:emissive_intensity", float(gen.uniform(0, 1000)))


# --- Writer --------------------------------------------------------------------------------------
writer = rep.WriterRegistry.get("KittiWriter")
writer.initialize(output_dir=data_dir, omit_semantic_type=True, semantic_filter_predicate="class:palletjack")
render_product = rep.create.render_product(cam.GetPath(), (args.width, args.height))
writer.attach(render_product)
print(f"[m3] writing {args.num_frames} frames to {data_dir}")

for i in range(args.num_frames):
    randomize()
    rep.orchestrator.step(rt_subframes=args.rt_subframes)
    if i % 10 == 0:
        print(f"[m3] frame {i}/{args.num_frames}")
rep.orchestrator.wait_until_complete()
writer.detach()
render_product.destroy()

# KittiWriter's semantic_filter_predicate is not applied to its *_fast bbox annotators in this build, so
# unlabelled warehouse geometry still gets "Unlabelled" rows. Keep only the class we train on.
det_dir = os.path.join(data_dir, "Camera", "object_detection")
for f in os.listdir(det_dir):
    path = os.path.join(det_dir, f)
    with open(path) as fh:
        rows = [line for line in fh if line.split(" ", 1)[0] == "palletjack"]
    with open(path, "w") as fh:
        fh.writelines(rows)

if args.test:
    cam_dir = os.path.join(data_dir, "Camera")
    labels = sorted(os.listdir(os.path.join(cam_dir, "object_detection")))
    classes, boxes = set(), set()
    for f in labels:
        with open(os.path.join(cam_dir, "object_detection", f)) as fh:
            rows = [line.split() for line in fh if line.strip()]
        classes.update(r[0] for r in rows)
        boxes.add(tuple(tuple(r[4:8]) for r in rows))
    n_rgb = len(os.listdir(os.path.join(cam_dir, "rgb")))
    print(f"[m3] rgb images: {n_rgb}, label files: {len(labels)}, classes: {sorted(classes)}, distinct label sets: {len(boxes)}")
    ok = n_rgb >= args.num_frames and classes <= {"palletjack"} and len(boxes) > 1
    print("[m3] PASS: randomized, palletjack-only KITTI data" if ok else "[m3] FAIL")
simulation_app.close()
