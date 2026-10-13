"""Build every course diagram: python3 learning_resource/diagrams/_build/build_diagrams.py [slug ...]"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dlib import Diagram  # noqa: E402

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = []


def diagram(*a, **k):
    d = Diagram(*a, **k)
    D.append(d)
    return d


# ---------------------------------------------------------------------------- course map
d = diagram("course-map", "Course map: five modules, one robot story", "Process · Course overview",
            "Course map showing Isaac Sim 6.1 feeding five modules: first robot, URDF import, synthetic data, "
            "software-in-the-loop and hardware-in-the-loop, each with its main artifact.")
d.node("isaac", 40, 280, 144, 112, "Isaac Sim 6.1", "./isaac-sim.sh", kind="input")
mods = [
    ("m1", "First robot", "mesh → drive → lidar", "simple_robot.usd", "M1", "focal"),
    ("m2", "URDF → USD", "import Carter", "carter.usda", "M2", "step"),
    ("m3", "Synthetic data", "Replicator SDG", "KITTI dataset", "M3", "step"),
    ("m4", "Software-in-loop", "OmniGraph + ROS 2", "/cmd_vel graph", "M4", "step"),
    ("m5", "Hardware-in-loop", "Jetson + Isaac ROS", "notes only", "M5", "optional"),
]
for i, (nid, name, sub, sub2, tag, kind) in enumerate(mods):
    d.node(nid, 216 + i * 208, 280, 176, 112, name, sub, tag=tag, kind=kind, sub2=sub2)
d.edge("isaac", "m1")
for a, b in [("m1", "m2"), ("m2", "m3"), ("m3", "m4"), ("m4", "m5")]:
    d.edge(a, b, dashed=(b == "m5"))
d.notes.append((216, 460, "Every lesson ends with a checkpoint script: ./python.sh learning_resource/scripts/<m*>.py --headless --test"))

# ---------------------------------------------------------------------------- 1.1 build ladder
d = diagram("m1-build-ladder", "Lesson 1.1 — from a mesh to a driving robot", "Process · Lesson 1.1",
            "Six steps that turn plain meshes into a driving robot: meshes, physics scene, rigid bodies, "
            "revolute joints, angular drives and an articulation root.")
steps = [
    ("mesh", "Meshes", "Create > Mesh", "Cube + 4 Cylinders", "input"),
    ("scene", "Physics scene", "gravity -Z 9.81", "+ Ground Plane", "step"),
    ("rigid", "Rigid bodies", "Add > Physics >", "Colliders Preset", "step"),
    ("joint", "Revolute joints", "axis Y", "rot1 = (-90, 0, 0)", "step"),
    ("drive", "Angular drives", "damping 10000", "target 50 °/s", "focal"),
    ("art", "Articulation", "root on", "SimpleRobot", "step"),
]
for i, (nid, name, sub, sub2, kind) in enumerate(steps):
    d.node(nid, 64 + i * 196, 288, 168, 112, name, sub, tag=f"STEP {i + 1}", kind=kind, sub2=sub2)
for a, b in zip(steps, steps[1:]):
    d.edge(a[0], b[0])
d.notes.append((64, 468, "Press Play after every step and watch what physics adds: nothing → falls → rests → wobbles → drives."))

# ---------------------------------------------------------------------------- 1.1 robot structure
d = diagram("m1-robot-structure", "Lesson 1.1 — SimpleRobot, seen from above", "Architecture · Lesson 1.1",
            "Top view of SimpleRobot: the Cube chassis is body 0 of four revolute joints whose body 1 is a wheel; "
            "the two rear wheels carry the angular drives.")
d.zone(160, 88, 920, 488, "SimpleRobot · Xform · Articulation Root")
d.node("cube", 520, 280, 240, 112, "Cube (chassis)", "rigid body", sub2="2 × 1 × 0.5 m", tag="BODY 0")
d.node("fl", 840, 120, 200, 96, "Front_Left_Wheel", "Ø 0.75 m · passive")
d.node("fr", 840, 456, 200, 96, "Front_Right_Wheel", "Ø 0.75 m · passive")
d.node("rl", 200, 120, 200, 96, "Rear_Left_Wheel", "drive 50 °/s", kind="focal")
d.node("rr", 200, 456, 200, 96, "Rear_Right_Wheel", "drive 50 °/s", kind="focal")
d.edge("cube", "fl", "r", "b", label="Front_Left_Joint", sf=0.25)
d.edge("cube", "fr", "r", "t", label="Front_Right_Joint", sf=0.75, label_side="below")
d.edge("cube", "rl", "l", "b", label="Rear_Left_Joint", sf=0.25)
d.edge("cube", "rr", "l", "t", label="Rear_Right_Joint", sf=0.75, label_side="below")
d.notes.append((1100, 340, "forward +X →"))
d.notes.append((1100, 140, "+Y = left"))

# ---------------------------------------------------------------------------- 1.2 differential controller
d = diagram("m1-diff-controller", "Lesson 1.2 — the Differential Controller graph", "Data flow · Lesson 1.2",
            "Action Graph built by Tools > Robotics > OmniGraph Controllers > Differential Controller: keyboard keys become "
            "linear and angular velocity, the controller turns them into wheel speeds and the articulation controller "
            "drives the rear joints every frame.")
d.node("kb", 40, 120, 176, 96, "Keyboard", "W A S D", kind="input")
d.node("keys", 256, 120, 208, 96, "Keys → speed", "ToDouble · Add", sub2="ScaleLinear/Angular")
d.node("diff", 504, 120, 240, 96, "Differential Controller", "r 0.375 · d 1.5", kind="focal")
d.node("art", 784, 120, 224, 96, "Articulation Ctrl", "velocityCommand")
d.node("joints", 1048, 120, 192, 96, "Rear joints", "Rear_Left_Joint", sub2="Rear_Right_Joint", kind="store")
d.node("tick", 504, 360, 240, 96, "On Playback Tick", "fires every frame")
d.node("names", 1048, 360, 192, 96, "ArrayNames", "Make Array (token[])")
d.edge("kb", "keys")
d.edge("keys", "diff")
d.edge("diff", "art")
d.edge("art", "joints")
d.edge("tick", "diff", "t", "b", label="EXEC")
d.edge("tick", "art", "r", "b", df=0.25, label="EXEC", label_seg=1)
d.edge("names", "art", "l", "b", df=0.75, label="JOINT NAMES", label_seg=1)

# ---------------------------------------------------------------------------- 1.3 sensor mounting
d = diagram("m1-sensor-mount", "Lesson 1.3 — where to mount each sensor in 6.1", "Flowchart · Lesson 1.3",
            "Decision flow for mounting sensors on SimpleRobot in Isaac Sim 6.1: cameras and the deprecated PhysX lidar "
            "may sit on the fixed-jointed Front_Sensor body, but an RTX lidar must sit directly under the chassis body "
            "and above the wheel tops.")
d.node("new", 40, 296, 176, 96, "New sensor", kind="input")
d.node("which", 256, 296, 160, 96, "Which sensor?")
d.node("cam", 520, 96, 280, 96, "Front_Sensor body", "rigid body + Fixed Joint")
d.node("trap", 872, 96, 360, 96, "RTX lidar here: no data", "topic exists, 0 messages", kind="boundary")
d.node("rtx", 520, 296, 280, 96, "Under chassis body", "select Cube → Create >", sub2="Sensors > RTX Lidar", kind="focal")
d.node("high", 840, 296, 176, 96, "Above wheels?", "z > 0.75 m", sub2="else raise it")
d.node("ok", 1056, 296, 176, 96, "/scan_lidar", "LaserScan ~10 Hz")
d.node("physx", 520, 496, 280, 96, "Front_Sensor body", "PhysX Lidar", sub2="(deprecated)", kind="optional")
d.edge("new", "which")
d.edge("which", "cam", "t", "l", label="CAMERA", label_seg=1)
d.edge("which", "rtx", label="RTX LIDAR")
d.edge("which", "physx", "b", "l", label="PHYSX LIDAR", label_seg=1)
d.edge("cam", "trap", dashed=True)
d.edge("rtx", "high")
d.edge("high", "ok")

# ---------------------------------------------------------------------------- 1.4 ROS 2 lidar flow
d = diagram("m1-ros2-lidar", "Lesson 1.4 — RTX lidar to RViz over ROS 2", "Architecture · Lesson 1.4",
            "Data path built by Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar: the playback tick renders the RTX lidar "
            "into a render product, the ROS2 RTX Lidar Helper publishes a LaserScan on /scan_lidar, and RViz2 draws it.")
d.zone(40, 64, 760, 480, "Isaac Sim process · Action Graph ROS2_LidarStream")
d.zone(840, 64, 400, 480, "ROS 2 Jazzy · your terminal")
d.node("tick", 72, 120, 200, 96, "On Playback Tick")
d.node("once", 312, 120, 200, 96, "Run One Frame", "RunOneSimulationFrame")
d.node("lidar", 72, 360, 200, 96, "RTX Lidar", "Example_Rotary_2D", kind="input")
d.node("rp", 312, 360, 200, 96, "Render Product", "CreateRenderProduct")
d.node("helper", 552, 240, 224, 96, "ROS2 RTX Lidar Helper", "type laser_scan", sub2="frame sim_lidar", kind="focal")
d.node("topic", 872, 240, 200, 96, "/scan_lidar", "LaserScan", sub2="best-effort QoS", kind="store")
d.node("rviz", 872, 424, 200, 96, "RViz2", "Fixed Frame sim_lidar", kind="external")
d.edge("tick", "once")
d.edge("once", "helper", "r", "t")
d.edge("lidar", "rp")
d.edge("rp", "helper", "r", "b")
d.edge("helper", "topic", style="link", label="DDS")
d.edge("topic", "rviz", "b", "t", style="link", label="SUBSCRIBE")

# ---------------------------------------------------------------------------- 2.1 URDF pipeline
d = diagram("m2-urdf-pipeline", "Lesson 2.1 — URDF to a drivable USD robot", "Process · Lesson 2.1",
            "Pipeline for importing Carter in Isaac Sim 6.1: the URDF goes through File > Import with Base Type Mobile, "
            "becomes carter.usda with payloads and a Physics variant set, the physx variant must be selected and the wheel "
            "drives configured before a controller can move it.")
d.node("urdf", 40, 120, 176, 112, "carter.urdf", "+ meshes/*.obj", kind="input")
d.node("imp", 256, 120, 200, 112, "URDF importer", "File > Import", sub2="Base Type: Mobile")
d.node("usd", 496, 120, 200, 112, "carter.usda", "+ payloads/", sub2="Physics variant set", kind="store")
d.node("var", 736, 120, 224, 112, "Physics variant", "select: physx", kind="focal")
d.node("drv", 1000, 120, 232, 112, "Wheel drives", "wheels: damping 10000", sub2="casters: 0 / 0")
d.node("trap", 496, 392, 200, 96, "No variant picked", "no physics at all", kind="boundary")
d.node("other", 736, 392, 224, 96, "Other variants", "mujoco · physics · none", kind="optional")
d.node("ctrl", 1000, 392, 232, 96, "Diff. Controller", "lesson 2.2")
d.edge("urdf", "imp")
d.edge("imp", "usd")
d.edge("usd", "var")
d.edge("var", "drv")
d.edge("usd", "trap", "b", "t", sf=0.3, df=0.3, dashed=True, label="IF SKIPPED")
d.edge("usd", "other", "b", "t", sf=0.7, mid=300, dashed=True)
d.edge("drv", "ctrl", "b", "t", label="DRIVE IT")

# ---------------------------------------------------------------------------- 2.1 carter structure
d = diagram("m2-carter-structure", "Lesson 2.1 — what the 6.1 importer writes", "Tree · Lesson 2.1",
            "Hierarchy of the imported carter.usda: links live under Geometry with chassis_link as articulation root, "
            "joints live under Physics, and a Physics variant set chooses the engine layer.")
d.node("root", 520, 56, 240, 80, "carter", "default prim", kind="input")
d.node("geo", 160, 196, 240, 80, "Geometry", "links (rigid bodies)")
d.node("phy", 520, 196, 240, 80, "Physics", "joints")
d.node("var", 880, 196, 240, 80, "Physics variants", "physx · mujoco · physics", kind="store")
d.node("chassis", 160, 336, 240, 80, "chassis_link", "rigid body · art. root", kind="focal")
d.node("dj", 440, 336, 240, 80, "left/right_wheel", "revolute · axis Y · driven")
d.node("cj", 720, 336, 240, 80, "rear_pivot / rear_axle", "revolute · passive")
d.node("wl", 40, 476, 240, 80, "left/right_wheel_link", "Ø 0.48 m")
d.node("cl", 320, 476, 240, 80, "rear_pivot_link", "→ rear_wheel_link")
d.edge("root", "geo", "b", "t", sf=0.25, mid=166)
d.edge("root", "phy", "b", "t")
d.edge("root", "var", "b", "t", sf=0.75, mid=166)
d.edge("geo", "chassis", "b", "t")
d.edge("phy", "dj", "b", "t", sf=0.3, mid=306)
d.edge("phy", "cj", "b", "t", sf=0.7, mid=306)
d.edge("chassis", "wl", "b", "t", sf=0.3, mid=446)
d.edge("chassis", "cl", "b", "t", sf=0.7, mid=446)

# ---------------------------------------------------------------------------- 2.2 carter drive
d = diagram("m2-carter-drive", "Lesson 2.2 — where the controller numbers come from", "Data flow · Lesson 2.2",
            "The Differential Controller parameters for Carter come straight from the URDF: wheel radius 0.24 m from the "
            "wheel cylinder and wheel distance 0.6284 m from the joint offsets; keyboard input then drives left_wheel and "
            "right_wheel through the articulation controller, clamped to 0.5 m/s.")
d.node("rad", 40, 120, 240, 96, "Wheel cylinder", "radius 0.240", sub2="carter.urdf", kind="store")
d.node("off", 40, 336, 240, 96, "Wheel joint origins", "y = ±0.3142", sub2="carter.urdf", kind="store")
d.node("diff", 360, 216, 280, 112, "Differential Controller", "wheelRadius 0.24", sub2="wheelDistance 0.6284", kind="focal")
d.node("kb", 400, 456, 200, 96, "W A S D", "keyboard graph", kind="input")
d.node("art", 720, 216, 240, 112, "Articulation Ctrl", "left_wheel", sub2="right_wheel")
d.node("car", 1000, 216, 232, 112, "Carter drives", "≤ 0.5 m/s", sub2="≤ 1.0 rad/s")
d.edge("rad", "diff", "r", "l", df=0.3, mid=320)
d.edge("off", "diff", "r", "l", df=0.7, mid=320)
d.edge("kb", "diff", "t", "b")
d.edge("diff", "art")
d.edge("art", "car")

# ---------------------------------------------------------------------------- 2.3 carter sensors
d = diagram("m2-carter-sensors", "Lesson 2.3 — sensors on the imported Carter", "Architecture · Lesson 2.3",
            "Camera and RTX lidar mounted directly under Carter's chassis_link body; the camera feeds a viewport, the lidar "
            "sees every rendered obstacle, and colliders on the obstacles only matter for physical contact.")
d.node("chassis", 72, 248, 240, 112, "chassis_link", "rigid body", sub2="articulation root", kind="focal")
d.node("cam", 400, 120, 240, 96, "RGB_Sensor", "translate 0.1, 0, 0.33", sub2="rotate 90, -90, 0")
d.node("lid", 400, 392, 240, 96, "RTX Lidar", "Example Rotary 2D", sub2="translate -0.05, 0, 0.42")
d.node("view", 728, 120, 240, 96, "Viewport", "Cameras > RGB_Sensor", kind="external")
d.node("obs", 728, 392, 240, 96, "Obstacles", "cubes · spheres", sub2="+ colliders for contact", kind="input")
d.node("ros", 1000, 392, 232, 96, "ROS 2 / RViz", "lesson 1.4 graph", kind="optional")
d.edge("chassis", "cam", "r", "l", sf=0.3, mid=356)
d.edge("chassis", "lid", "r", "l", sf=0.7, mid=356)
d.edge("cam", "view", label="IMAGE")
d.edge("lid", "obs", label="RAYS")
d.edge("obs", "ros", dashed=True)

# ---------------------------------------------------------------------------- 2.4 nova carter
d = diagram("m2-nova-carter", "Lesson 2.4 — Nova Carter's ready-made sensor suite", "Tree · Lesson 2.4",
            "Hierarchy of NVIDIA's Nova Carter in Isaac Sim 6.1: chassis_link is the articulation root carrying two 2D lidars, "
            "an XT-32 3D lidar, four Hawk stereo cameras, four Owl fisheye cameras, and the driven and caster joints.")
d.node("root", 520, 48, 240, 80, "nova_carter", "Create > Robots", kind="input")
d.node("ch", 520, 168, 240, 80, "chassis_link", "articulation root", kind="focal")
d.node("sens", 240, 296, 240, 80, "sensors/", "under the body")
d.node("drive", 760, 296, 216, 80, "Drive joints", "joint_wheel_left/right")
d.node("cast", 1016, 296, 216, 80, "Caster joints", "swing + caster ×2", kind="optional")
d.node("l2d", 40, 440, 200, 96, "2D lidars ×2", "RPLidar S2E", sub2="front · rear", kind="store")
d.node("l3d", 264, 440, 200, 96, "3D lidar", "Hesai XT-32", sub2="10 Hz", kind="store")
d.node("hawk", 488, 440, 200, 96, "Hawk ×4", "stereo + IMU", kind="store")
d.node("owl", 712, 440, 200, 96, "Owl ×4", "fisheye cameras", kind="store")
d.edge("root", "ch", "b", "t")
d.edge("ch", "sens", "b", "t", sf=0.3, mid=272)
d.edge("ch", "drive", "b", "t", sf=0.6, mid=276)
d.edge("ch", "cast", "b", "t", sf=0.85, mid=260)
# the further right a child is, the higher its horizontal run, so no runs overlap or cross
for i, (c, m) in enumerate([("l2d", 408), ("l3d", 424), ("hawk", 412), ("owl", 396)]):
    d.edge("sens", c, "b", "t", sf=0.2 + 0.2 * i, mid=m)

# ---------------------------------------------------------------------------- 3 SDG pipeline
d = diagram("m3-sdg-pipeline", "Module 3 — pallet-jack dataset with Replicator (6.1)", "Data flow · Module 3",
            "Synthetic data pipeline: load the warehouse, add pallet jacks and distractors, keep labels only on pallet jacks, "
            "set up camera and KittiWriter, then per frame randomize with the functional API, step the orchestrator and "
            "write a KITTI dataset used to train a detector.")
d.node("wh", 40, 120, 200, 96, "warehouse.usd", "Simple_Warehouse", kind="input")
d.node("add", 280, 120, 200, 96, "Add assets", "6 pallet jacks", sub2="12 distractors")
d.node("lab", 520, 120, 200, 96, "Fix labels", "block warehouse", sub2="label palletjack")
d.node("wr", 760, 120, 200, 96, "Camera + writer", "KittiWriter", sub2="960 × 544")
d.node("rand", 280, 400, 200, 96, "randomize()", "camera · poses · lights", sub2="floor/wall textures", kind="focal")
d.node("step", 520, 400, 200, 96, "orchestrator.step", "rt_subframes=4")
d.node("ds", 760, 400, 200, 96, "Camera/ dataset", "rgb/ · object_detection/", sub2="palletjack rows only", kind="store")
d.node("train", 1000, 400, 232, 96, "Train detector", "TAO / PyTorch", kind="external")
d.edge("wh", "add")
d.edge("add", "lab")
d.edge("lab", "wr")
d.edge("wr", "rand", "b", "t", mid=300, label="FOR N FRAMES")
d.edge("rand", "step")
d.edge("step", "ds")
d.edge("ds", "train")
d.edge("step", "rand", "b", "b", mid=560, dashed=True, label="NEXT FRAME")

# ---------------------------------------------------------------------------- 4.1 cmd_vel
d = diagram("m4-cmd-vel", "Lesson 4.1 — driving Nova Carter from /cmd_vel", "Data flow · Lesson 4.1",
            "ROS 2 to Isaac Sim control loop: teleop_twist_keyboard publishes geometry_msgs/Twist on /cmd_vel, the Action "
            "Graph subscribes, splits linear.x and angular.z, the Differential Controller computes wheel speeds and the "
            "Articulation Controller drives joint_wheel_left and joint_wheel_right.")
d.zone(40, 48, 296, 560, "ROS 2 Jazzy (system)")
d.zone(360, 48, 880, 560, "Isaac Sim · Action Graph")
d.node("tele", 56, 200, 264, 96, "teleop_twist_keyboard", "i , j l k", kind="input")
d.node("tick", 400, 88, 200, 80, "Tick + ROS2 Context", kind="store")
d.node("sub", 400, 200, 200, 96, "Subscribe Twist", "topicName cmd_vel")
d.node("brk", 640, 200, 176, 96, "Break 3-Vector ×2", "linear.x", sub2="angular.z")
d.node("diff", 856, 200, 224, 96, "Diff. Controller", "r 0.14 · d 0.413", sub2="max 2.0 / 3.0", kind="focal")
d.node("art", 848, 440, 240, 96, "Articulation Controller", "target chassis_link")
d.node("joints", 440, 440, 320, 96, "joint_wheel_left / right", "velocity targets", kind="store")
d.edge("tele", "sub", style="link", label="cmd_vel")
d.edge("tick", "sub", "b", "t")
d.edge("sub", "brk")
d.edge("brk", "diff")
d.edge("diff", "art", "b", "t")
d.edge("art", "joints", "l", "r", label="VELOCITY")

# ---------------------------------------------------------------------------- 4.2 python layers
d = diagram("m4-python-layers", "Lesson 4.2 — the Python layers you script against", "Layer stack · Lesson 4.2",
            "Layer stack of Isaac Sim 6.1 scripting: your script on top of isaacsim.core.experimental, Kit and omni services, "
            "OpenUSD pxr APIs and the PhysX and RTX engines; omni.isaac.core is removed and isaacsim.core.api deprecated.")
layers = [
    ("app", "Your script", "SimulationApp (standalone)  ·  Window > Script Editor (in the GUI)", "input"),
    ("exp", "isaacsim.core.experimental", "Cube · GroundPlane · RigidPrim · GeomPrim · Articulation · sensors", "focal"),
    ("kit", "Kit / omni", "omni.usd · omni.kit.commands · omni.timeline · omni.graph (OmniGraph)", "step"),
    ("usd", "OpenUSD  (pxr)", "Usd · UsdGeom · UsdPhysics · PhysxSchema — stable across versions", "step"),
    ("eng", "Engines", "PhysX (or Newton) physics · RTX renderer · RTX sensors", "external"),
]
for i, (nid, name, sub, kind) in enumerate(layers):
    d.node(nid, 40, 56 + i * 112, 840, 88, name, sub, kind=kind)
d.node("old", 1000, 168, 240, 88, "omni.isaac.core", "4.x · removed", kind="optional")
d.node("dep", 1000, 280, 240, 88, "isaacsim.core.api", "5.x · deprecated", kind="optional")
d.edge("old", "exp", "l", "r", dashed=True, label="REPLACED BY")
d.edge("dep", "exp", "l", "r", dashed=True, sf=0.5, df=0.85, mid=940)

# ---------------------------------------------------------------------------- 4.3 SIL segmentation
d = diagram("m4-sil-segmentation", "Lesson 4.3 — software-in-the-loop with Isaac ROS", "Architecture · Lesson 4.3",
            "Software-in-the-loop setup: Isaac Sim publishes a Hawk camera image on /rgb through the ROS 2 Camera graph, "
            "an Isaac ROS segmentation container processes it, and your ROS node can send /cmd_vel back to the drive graph.")
d.zone(40, 64, 520, 480, "Isaac Sim 6.1")
d.zone(680, 64, 560, 480, "ROS 2 · Isaac ROS (Docker)")
d.node("cam", 72, 120, 200, 96, "Hawk camera", "front_hawk/left", kind="input")
d.node("graph", 312, 120, 216, 96, "ROS 2 Camera graph", "Tools > ROS 2 OmniGraphs")
d.node("drive", 312, 400, 216, 96, "Diff drive graph", "lesson 4.1")
d.node("seg", 712, 120, 240, 96, "Isaac ROS segmentation", "GPU · container", kind="focal")
d.node("view", 992, 120, 232, 96, "rqt_image_view", "/segmentation", kind="external")
d.node("node", 712, 400, 240, 96, "Your ROS node", "teleop · Nav2 · logic", kind="input")
d.edge("cam", "graph")
d.edge("graph", "seg", style="link", label="/rgb")
d.edge("seg", "view", style="link")
d.edge("seg", "node", "b", "t", dashed=True, label="RESULTS")
d.edge("node", "drive", "l", "r", style="link", label="/cmd_vel")

# ---------------------------------------------------------------------------- 5 HIL
d = diagram("m5-hil", "Module 5 — hardware-in-the-loop with a Jetson", "Deployment · Module 5",
            "Hardware-in-the-loop deployment: the workstation runs Isaac Sim 6.1 with ROS 2 graphs, a LAN carries DDS traffic "
            "with matching ROS_DOMAIN_ID and RMW, and the Jetson runs Isaac ROS and your perception or Nav2 nodes using "
            "simulated time, sending /cmd_vel back.")
d.zone(40, 64, 440, 480, "Workstation · Ubuntu 24.04")
d.zone(800, 64, 440, 480, "Jetson · JetPack")
d.node("isaac", 72, 120, 224, 96, "Isaac Sim 6.1", "bundled ROS 2 Jazzy")
d.node("graphs", 72, 360, 224, 96, "ROS 2 graphs", "clock · scan · rgb", sub2="sub: cmd_vel")
d.node("net", 520, 248, 240, 96, "LAN · DDS", "same ROS_DOMAIN_ID", sub2="rmw_fastrtps_cpp", kind="external")
d.node("ros", 832, 120, 240, 96, "Isaac ROS", "container (often Humble)", kind="focal")
d.node("app", 832, 360, 240, 96, "Perception / Nav2", "use_sim_time: true", kind="input")
d.edge("isaac", "graphs", "b", "t")
d.edge("graphs", "net", "r", "l", sf=0.3, df=0.3, mid=400, style="link", label="SENSORS", label_seg=0)
d.edge("net", "graphs", "l", "r", sf=0.7, df=0.7, mid=440, style="link", dashed=True)
d.edge("net", "ros", "r", "l", style="link", mid=796)
d.edge("ros", "app", "b", "t")
d.edge("app", "net", "l", "b", style="link", dashed=True, label="/cmd_vel")

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for d in D:
        if only and d.slug not in only:
            continue
        print("built", d.write(OUT))
