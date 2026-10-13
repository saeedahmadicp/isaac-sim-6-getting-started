"""Add tutorial sections (video, diagrams, concepts, checks, exercises, quiz) to every lesson file.

Idempotent: everything it adds sits between <!-- tutorial:start --> / <!-- tutorial:end --> markers
(top block) and <!-- practice:start --> / <!-- practice:end --> (bottom block), and is replaced on re-run.

    python3 learning_resource/tools/build_tutorial_sections.py

WARNING: this was a one-off generator. The lessons have since been edited by hand, and re-running it
replaces everything between the markers with the text below. Only run it if you edit the text here.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # learning_resource

L = {}

L["module1_first_robot/lesson1_building_a_simple_robot.md"] = dict(
    video="1.1_building_a_simple_robot",
    diagrams=[("m1-build-ladder", "The six-step ladder from mesh to driving robot"),
              ("m1-robot-structure", "SimpleRobot from above: chassis, wheels and joints")],
    time="45–60 min",
    learn=["Navigate the viewport and read the Stage / Property panels",
           "Tell **visual meshes** from **physics** (rigid bodies, colliders, physics scene)",
           "Connect bodies with **revolute joints** and drive them with **angular drives**",
           "Group bodies into an **articulation** that controllers can address"],
    concepts="""
**USD stage and prims.** Everything you see is a *prim* in a USD *stage* (the tree in the Stage panel). An
`Xform` is a transform-only container; `Mesh`, `Cylinder`, `Camera` are prims with geometry or function.
Moving a parent Xform moves all children — that is why `SimpleRobot` can lift the whole robot.

**Physics is opt-in.** A mesh is only pixels until you add APIs to it:

| API | What it adds | Without it |
|---|---|---|
| `PhysicsScene` | gravity, solver, time step | nothing moves at all |
| `RigidBodyAPI` | mass, velocity — the prim is simulated | prim is static |
| `CollisionAPI` | a collision shape (convex hull for the preset) | falls through everything |

**Joints and frames.** A joint connects *body 0* to *body 1*. Each side has a local frame
(`Local Position/Rotation 0/1`). A revolute joint spins around one axis of those frames — for a wheel
that must be the axle (Y here). The wheel cylinder is rotated 90° about X, so its own frame is turned;
`Local Rotation 1 = (-90, 0, 0)` turns the joint frame back so both frames agree.

**Drives.** An angular drive is a spring–damper on the joint:
`torque = stiffness · (target_pos − pos) + damping · (target_vel − vel)`.
Stiffness 0 + large damping = a **velocity motor** (it chases `Target Velocity`, in **deg/s**).
50 °/s on a 0.375 m wheel ≈ 0.33 m/s — which is exactly what the checkpoint script measures.

**Articulation.** An *articulation root* turns the bodies + joints into one reduced-coordinate chain
that the solver handles stably and that controllers address by joint name (lesson 1.2).
""",
    checks=[("Cube alone, Play", "nothing happens (no physics yet)"),
            ("Cube with rigid body, no ground", "falls forever"),
            ("Robot with joints, no drives", "rests on its wheels"),
            ("Rear drives at 50 °/s", "drives along +X at ≈ 0.33 m/s"),
            ("`m1_build_simple_robot.py --headless --test`", "`[m1] PASS: robot drove forward`")],
    exercises=["Set the rear drives to **+50 / −50 °/s**. What happens, and why?",
               "Change the wheel scale to 1.0 (Ø 1 m). Predict the new speed, then measure it "
               "(select Cube → Property → Rigid Body → Linear Velocity while playing).",
               "Add drives to the **front** joints too (4-wheel drive). Does it go faster? Why not?",
               "Swap Body 0 and Body 1 on one joint and watch what breaks — then undo it."],
    quiz=[("Why does a cube with only a Rigid Body (no collider) fall through the ground?",
           "Collisions need a collision shape on both prims; the rigid body only adds dynamics."),
          ("Stiffness 0, damping 10000, target velocity 50 — position or velocity drive?",
           "Velocity drive: with zero stiffness only the velocity error produces torque."),
          ("In what unit is the angular drive's Target Velocity?", "Degrees per second.")],
)

L["module1_first_robot/lesson2_controlling_the_robot.md"] = dict(
    video="1.2_controlling_the_robot",
    diagrams=[("m1-diff-controller", "The Differential Controller Action Graph")],
    time="30 min",
    learn=["Read an **Action Graph** (OmniGraph): execution vs data connections",
           "Use the **Differential Controller** tool to generate a graph",
           "Map keyboard input to robot velocity"],
    concepts="""
**OmniGraph / Action Graphs.** Visual programs stored in the stage. *Execution* wires (white) say
*when* a node runs; *data* wires carry values. `On Playback Tick` fires once per simulated frame, so
anything connected to it runs every frame while the timeline plays — and never while stopped.

**Differential drive kinematics.** For wheel radius *r* and track width *d*, a body velocity
(*v* forward, *ω* turning) becomes wheel speeds

```
ω_left  = (v − ω·d/2) / r
ω_right = (v + ω·d/2) / r
```

That is all the `Differential Controller` node computes. Wrong *r* or *d* doesn't break the robot — it
just makes it drive at the wrong speed or turn by the wrong angle.

**Articulation Controller.** Takes per-joint commands (position, velocity or effort arrays) plus joint
names and writes them as drive targets on the articulation. It needs the articulation root to find joints.
""",
    checks=[("Play with Linear Velocity 0", "robot stands still"),
            ("Linear Velocity 1", "drives forward ≈ 1 m/s"),
            ("Angular Velocity 1", "turns left (counter-clockwise from above)"),
            ("Keyboard graph, hold W", "drives forward; A/D turn")],
    exercises=["Set *distance between wheels* to 3.0 instead of 1.5 and command ω = 1 rad/s. "
               "Does the robot turn faster or slower than 1 rad/s? Explain with the formula.",
               "Make **Shift+W** a faster forward key (the keyboard nodes accept a modifier).",
               "Add the front joints to `ArrayNames` (4 names) and feed the controller output twice — "
               "what has to change in the graph?"],
    quiz=[("Why does nothing happen in the graph while the simulation is stopped?",
           "Everything hangs off On Playback Tick, which only fires while the timeline plays."),
          ("What does the Articulation Controller need in order to find the joints?",
           "An articulation root on the robot (and the joint names)."),
          ("v = 1 m/s, ω = 0, r = 0.375 m — wheel speed?", "1 / 0.375 ≈ 2.67 rad/s on both wheels.")],
)

L["module1_first_robot/lesson3_adding_sensors.md"] = dict(
    video="1.3_adding_sensors",
    diagrams=[("m1-sensor-mount", "Where each sensor goes in Isaac Sim 6.1")],
    time="45 min",
    learn=["Mount a **camera** on a fixed-jointed sensor body",
           "Add an **RTX lidar** (the 6.1 replacement of the PhysX lidar) in a place where it works",
           "Understand how RTX sensors see the scene (rendering, not physics)"],
    concepts="""
**Two kinds of lidar.** The course's *PhysX lidar* casts physics rays — it only hits **colliders**.
Isaac Sim 6.1's *RTX lidar* is simulated by the RTX renderer — it hits **everything rendered**, models
real sensor scan patterns (vendor configs like Ouster, Hesai, SICK) and outputs a *GenericModelOutput*
buffer that helper nodes turn into `LaserScan` / `PointCloud2`.

**Sensors ride on bodies.** A sensor prim follows whatever body it is parented to. Under a rigid body it
moves with that body; under a plain Xform beside the bodies it stays behind when the robot drives off.

**The 6.1 trap.** An RTX lidar under a *separate* rigid body that is fixed-jointed to the chassis produced
no output in our tests (topic exists, zero messages). Under the chassis body itself it works. Nova Carter
mounts all its sensors that way (`chassis_link/sensors/...`), so do the same.

**Units under a scaled parent.** `Cube` is scaled (2, 1, 0.5). A child's Translate is multiplied by that
scale: `(0.45, 0, 1.0)` → 0.9 m forward, 0.5 m up. The ranges the lidar reports are still in metres
(verified: an obstacle 2.50 m ahead reads 2.50 m).
""",
    checks=[("Viewport → Cameras → Robot_Camera", "you see the scene from the robot's front"),
            ("Drive with W while in Viewport 2 = Robot_Camera", "camera view moves with the robot"),
            ("Lidar prim type in Property panel", "`OmniLidar`, under `/World/SimpleRobot/Cube`"),
            ("`m1_ros2_lidar.py --headless --test`", "`forward beam = 2.50 m … PASS`")],
    exercises=["Lower the lidar to Translate z = 0.7 and look at the scan in RViz (lesson 1.4). "
               "Where do the extra close points come from?",
               "Swap *Example Rotary 2D* for **Create > Sensors > RTX Lidar > Ouster > OS1** and publish "
               "*Point Cloud* instead of *Laser Scan*.",
               "Put a cone behind a glass-like thin plane without a collider. Which lidar type would see "
               "the plane — PhysX or RTX?"],
    quiz=[("Does an RTX lidar need colliders on obstacles to detect them?",
           "No — it renders the scene; colliders only matter for physical contact."),
          ("Where must the RTX lidar be mounted on SimpleRobot in 6.1?",
           "Directly under the chassis rigid body (Cube), not on the fixed-jointed Front_Sensor."),
          ("Why place the lidar above 0.75 m?", "Below the wheel tops the scan hits the robot's own wheels.")],
)

L["module1_first_robot/lesson4_ros2_and_rviz.md"] = dict(
    video="1.4_ros2_and_rviz",
    diagrams=[("m1-ros2-lidar", "RTX lidar → ROS 2 LaserScan → RViz")],
    time="45 min (+ ROS 2 install)",
    learn=["Publish simulated sensor data on **ROS 2** topics",
           "Inspect topics with the `ros2` CLI and visualise them in **RViz2**",
           "Understand frames, QoS and domain IDs — the three usual reasons for 'no data'"],
    concepts="""
**ROS 2 in one paragraph.** Programs (*nodes*) exchange typed *messages* on named *topics* through DDS.
Nodes find each other automatically when they share a `ROS_DOMAIN_ID` and a compatible middleware (RMW).
Isaac Sim's bridge is just another node living inside the simulator.

**Frames.** Every sensor message carries `header.frame_id`. RViz draws data relative to its *Fixed
Frame*; if no transform connects the two, nothing is drawn. With only one frame (`sim_lidar`), set the
Fixed Frame to exactly that name.

**QoS.** Sensor streams are published *best-effort* (drop old data rather than queue it). `rviz2` and
`ros2 topic echo` adapt automatically; your own subscriber must use `qos_profile_sensor_data`.

**Bundled vs system ROS.** Isaac Sim loads its own Jazzy libraries (`exts/isaacsim.ros2.core/jazzy`).
System ROS is only needed for tools you run outside — and must be sourced in *those* terminals.
""",
    checks=[("`ros2 topic list` while playing", "`/scan_lidar` is listed"),
            ("`ros2 topic hz /scan_lidar`", "≈ 10 Hz"),
            ("`ros2 topic echo /scan_lidar --once`", "`frame_id: sim_lidar`, 3600 ranges"),
            ("RViz, Fixed Frame `sim_lidar`, LaserScan display", "points on your obstacles")],
    exercises=["Tick *Point Cloud* in the RTX Lidar graph dialog too and add a **PointCloud2** display in RViz.",
               "Run `export ROS_DOMAIN_ID=7` in the RViz terminal only. What happens? Fix it.",
               "Write a 15-line rclpy node that prints the closest range in front of the robot "
               "(remember `qos_profile_sensor_data`)."],
    quiz=[("RViz says 'Frame [sim_lidar] does not exist'. What do you change?",
           "Set Global Options → Fixed Frame to `sim_lidar` (the frame id, not the topic)."),
          ("Do you need to source /opt/ros/jazzy before ./isaac-sim.sh?", "No — 6.1 uses its bundled Jazzy libraries."),
          ("`ros2 topic echo` shows data but your node gets nothing. Likely cause?",
           "QoS mismatch: subscribe with the sensor-data (best-effort) profile.")],
)

L["module2_urdf_carter/lesson1_importing_urdf.md"] = dict(
    video="2.1_importing_urdf",
    diagrams=[("m2-urdf-pipeline", "URDF → drivable USD robot in 6.1"),
              ("m2-carter-structure", "What the 6.1 importer writes")],
    time="30 min",
    learn=["Import a **URDF** with the rewritten 6.1 importer",
           "Understand the generated asset: payloads, **Physics variant set**, Geometry vs Physics scopes",
           "Configure joint **drives** by hand (the 6.1 dialog no longer does it)"],
    concepts="""
**URDF vs USD.** URDF (ROS) describes *links* (rigid parts with visuals/collisions/inertia) and *joints*
(how links move relative to each other). USD describes a *scene*. The importer maps links → rigid body
Xforms under `Geometry`, joints → `PhysicsRevoluteJoint`/… under `Physics`.

**Layered assets.** The 6.1 converter writes `carter.usda` (the entry file) plus `payloads/`
(`base`, `geometries`, `materials`, `Physics/physx|mujoco|physics`). Layers let one asset carry several
physics descriptions; a **variant set** called `Physics` chooses which one is loaded. No selection = no
physics layer = a robot that neither falls nor moves.

**Drives after import.** URDF has no notion of "this joint is motorised with gain X", so the importer
creates angular drives with zero gains. You decide: wheels → velocity drives (stiffness 0, damping > 0),
casters → passive (both 0).
""",
    checks=[("Stage panel after import", "`carter > Geometry`, `Physics`, `Materials`"),
            ("carter → Property → Variants", "Physics = **physx**"),
            ("left_wheel → Drive", "stiffness 0, damping 10000"),
            ("`m2_import_carter.py --headless --test`", "`[m2] PASS: Carter drove forward`")],
    exercises=["Open `learning_resource/output/carter/payloads/Physics/physics.usda` in a text editor and find "
               "the `left_wheel` joint. Which body is body0?",
               "Switch the variant to **mujoco** and press Play. What happens with the PhysX engine running?",
               "Re-import with *Base Type = Fixed*. What changed in `Physics/`?"],
    quiz=[("The imported Carter doesn't fall when you press Play. First thing to check?",
           "The Physics variant — select physx."),
          ("Where are the joints in the 6.1 asset?", "Under `/carter/Physics/`."),
          ("Which gains make a joint a velocity drive?", "Stiffness 0 and damping > 0.")],
)

L["module2_urdf_carter/lesson2_preparing_the_simulation.md"] = dict(
    video="2.2_preparing_the_simulation",
    diagrams=[("m2-carter-drive", "Where the Differential Controller numbers come from")],
    time="30 min",
    learn=["Compose a scene from referenced assets",
           "Read controller parameters straight out of the URDF",
           "Limit speeds so a controller behaves"],
    concepts="""
**References.** Dragging `carter.usda` into a stage creates a *reference*: the robot's data stays in its
file, your scene stores only "load that file here" plus your overrides (position, variant choice, drive
gains you change later). That's why the variant must be selected again per reference.

**Parameters from the source.** The controller needs wheel radius and track width. Don't guess — the URDF
says: wheel `<cylinder radius="0.240">` and wheel joints at `y = ±0.3142` → track 0.6284 m.

**Saturation.** Keyboard graphs command step changes; without `maxLinearSpeed` / `maxAngularSpeed` the
wheels saturate, slip and the robot hops. Limits are a cheap way to keep a sim stable.
""",
    checks=[("Play after adding the reference", "Carter drops onto the grid and rests"),
            ("Both wheel targets 20 °/s", "≈ 0.08 m/s straight"),
            ("Keyboard graph, hold W", "≤ 0.5 m/s (chassis_link → Rigid Body velocity)")],
    exercises=["Set *wheel radius* to 0.12 (half the real value) and drive forward at 0.2 m/s. Measure the "
               "real speed. Why is it double?",
               "Make the casters slightly damped (damping 10). Is turning smoother or worse?",
               "Save the scene, close Isaac Sim, edit `carter.usda`'s drive gains in a text editor and reopen — "
               "does your scene pick up the change? (That's what references buy you.)"],
    quiz=[("Why must the physics variant be selected again in a new scene?",
           "The selection is an override stored on the referencing prim, not in carter.usda."),
          ("Where does wheelDistance 0.6284 come from?", "2 × the wheel joint y-offset 0.3142 in the URDF."),
          ("Why limit maxLinearSpeed?", "Keyboard steps saturate the wheels and make the robot slip and hop.")],
)

L["module2_urdf_carter/lesson3_adding_sensors.md"] = dict(
    video="2.3_adding_sensors",
    diagrams=[("m2-carter-sensors", "Sensors on the imported Carter")],
    time="30 min",
    learn=["Apply the module-1 sensor rules to an imported robot",
           "Edit a referenced asset (and know when your edits land in which file)"],
    concepts="""
**Where do edits go?** Adding a prim under a *referenced* robot writes an override into your **scene**
file, not into `carter.usda`. Usually that's what you want (the sensor belongs to this experiment). To make
the sensor part of the robot asset, open `carter.usda` itself and add it there.

**Sensor frames.** Camera prims look down their local −Z with +Y up; the course's rotation `(90, −90, 0)`
turns that into "look along the robot's +X". If an image is sideways, it's always this rotation.
""",
    checks=[("Viewport → Cameras → RGB_Sensor", "view from Carter's front"),
            ("Lidar prim path", "`…/chassis_link/Example_Rotary_2D`"),
            ("Drive into an obstacle with colliders", "Carter is stopped by it")],
    exercises=["Publish this lidar to ROS 2 (lesson 1.4 dialog) and view it in RViz while driving.",
               "Add a second camera looking backwards. Which rotation do you need?"],
    quiz=[("You added a camera under the referenced carter. Which file stores it?",
           "Your scene file (as an override), not carter.usda."),
          ("Why does the RTX lidar see obstacles without colliders?", "It is rendered, not physics-based.")],
)

L["module2_urdf_carter/lesson4_nova_carter.md"] = dict(
    video="2.4_nova_carter",
    diagrams=[("m2-nova-carter", "Nova Carter's ready-made sensor suite")],
    time="15 min",
    learn=["Load a production robot asset", "Read a real sensor suite and joint layout"],
    concepts="""
**Why prepared assets?** Nova Carter took NVIDIA engineers tuned masses, drive gains, collision shapes,
materials and calibrated sensor models. For real projects you start here and only build robots yourself
when no asset exists (then via URDF → USD as in lesson 2.1).

**Robot-type layout.** Notice the pattern you will see in most 6.x robots: one articulation root body,
`sensors/` as plain Xforms beneath it, joints named `joint_*`.
""",
    checks=[("Create > Robots > Nova Carter with Sensors", "`/World/nova_carter` appears"),
            ("Expand chassis_link/sensors", "front/rear RPLidar, XT_32, 4× Hawk, 4× Owl, chassis_imu")],
    exercises=["Look through `front_hawk/left/camera_left` (Viewport camera menu).",
               "Find the drive gains of `joint_wheel_left`. How do they compare with what you set on Carter?"],
    quiz=[("Which prim is Nova Carter's articulation root?", "`chassis_link`."),
          ("What type is the XT-32 prim?", "An RTX `OmniLidar`.")],
)

L["module3_sdg/lesson1_generate_dataset.md"] = dict(
    video="3.1_synthetic_data",
    diagrams=[("m3-sdg-pipeline", "Pallet-jack dataset pipeline (6.1)")],
    time="1 h (+ generation time)",
    learn=["Explain **domain randomization** and the sim-to-real gap",
           "Drive Replicator with the **functional API** (the 6.1 pattern)",
           "Produce and inspect a **KITTI** detection dataset"],
    concepts="""
**Why synthetic data?** Labelling thousands of real images is slow and expensive; a renderer knows the
exact box of every object, so labels are free and perfect.

**Domain randomization.** Randomise everything that should *not* matter (camera pose, lighting, textures,
distractors) so the model can only rely on what *does* matter (the pallet jack's shape). Two gaps to close:
*appearance* (rendering realism) and *content* (scene variety).

**Replicator, two styles.** *Graph* style (`with rep.trigger.on_frame(): rep.modify.pose(...)`) builds an
OmniGraph that runs inside the orchestrator. *Functional* style (`rep.functional.modify.pose(prim, ...)`)
changes the stage immediately in Python, then `rep.orchestrator.step()` renders and writes one frame.
On this 6.1 build the functional style was the reliable one.

**Writers and annotators.** Annotators compute per-frame data (rgb, bounding boxes, segmentation);
writers (KittiWriter, BasicWriter, …) save annotator outputs in a dataset format.
""",
    checks=[("`m3_palletjack_sdg.py --headless --test`", "`PASS: randomized, palletjack-only KITTI data`"),
            ("`Camera/rgb/*.png`", "different viewpoints, pallet jacks in varying colours/poses"),
            ("`Camera/object_detection/*.txt`", "only `palletjack` rows")],
    exercises=["Add a **DomeLight** with random intensity so fewer frames are dark.",
               "Add a second class (`class: cone` on the traffic cones) and keep both classes in the labels.",
               "Write a 10-line script that draws the KITTI boxes on `rgb/0.png` to check them visually."],
    quiz=[("Why randomize the floor texture when we only care about pallet jacks?",
           "So the detector cannot rely on the background — it must learn the object."),
          ("What does `rep.orchestrator.step()` do?", "Renders one frame and lets attached writers save it."),
          ("Why did the course's `update_semantics()` not remove the warehouse labels in 6.1?",
           "They come from referenced layers; RemoveProperty can't delete those — the script blocks them.")],
)

L["module4_sil/lesson1_omnigraph_cmd_vel.md"] = dict(
    video="4.1_omnigraph_cmd_vel",
    diagrams=[("m4-cmd-vel", "Driving Nova Carter from /cmd_vel")],
    time="45 min",
    learn=["Build a ROS 2 **subscriber** Action Graph by hand",
           "Drive a simulated robot from standard ROS tools (`ros2 topic pub`, teleop)",
           "Explain software-in-the-loop (SIL)"],
    concepts="""
**Software-in-the-loop.** The robot software runs unchanged; only its inputs (sensors) and outputs
(actuators) are connected to a simulator instead of hardware. `/cmd_vel` (`geometry_msgs/Twist`) is the
standard ROS interface for "drive with this velocity", so anything that drives a real mobile base
(teleop, Nav2, your planner) can drive the simulated one.

**Twist.** `linear.x` = forward m/s, `angular.z` = yaw rate rad/s; the other four fields are unused for a
differential-drive robot — hence the two *Break 3-Vector* nodes picking `x` and `z`.
""",
    checks=[("`ros2 topic list` while playing", "`/cmd_vel`"),
            ("`ros2 topic pub --once /cmd_vel … x: 0.2`", "Carter rolls forward"),
            ("`m4_nova_carter_cmd_vel.py --headless --test`", "`[m4] PASS: Nova Carter follows /cmd_vel`")],
    exercises=["Add an **Odometry** publisher (Tools > Robotics > ROS 2 OmniGraphs > Odometry Publisher) and "
               "watch `/odom` while driving.",
               "Publish `/cmd_vel` at 10 Hz with `ros2 topic pub -r 10 …` and stop the publisher. "
               "Does Carter keep driving? What would a real base do (watchdog)?"],
    quiz=[("Which two Twist fields does a differential-drive robot use?", "linear.x and angular.z."),
          ("What is the Articulation Controller's target for Nova Carter?", "`chassis_link`, the articulation root.")],
)

L["module4_sil/lesson2_python_scripting.md"] = dict(
    video="4.2_python_scripting",
    diagrams=[("m4-python-layers", "The Python layers you script against")],
    time="45 min",
    learn=["Run code in the **Script Editor** and as a **standalone app**",
           "Choose between raw **USD** and the **6.1 core API**",
           "Port 4.x `omni.isaac.core` code"],
    concepts="""
**Two ways to run Python.** *Script Editor*: inside the running GUI, shares its stage — good for poking.
*Standalone* (`./python.sh my.py`): your script owns the app loop via `SimulationApp`, can run headless,
and is how tests, data generation and RL run.

**Rule #1 of standalone scripts.** Create `SimulationApp(...)` **before** importing anything from
`isaacsim.*`/`omni.*` (those modules only exist once Kit is running).

**Which API?** Raw `pxr` USD is verbose but never changes between versions. `isaacsim.core.experimental`
is concise and batched (operate on many prims at once, NumPy/Torch/Warp arrays) — the 6.x way.
""",
    checks=[("USD snippet in Script Editor + Play", "cube falls and rests at z = 0.25"),
            ("Core API snippet in Script Editor + Play", "same"),
            ("`m4_run_snippet.py … --headless --test`", "`[m4] PASS: cube fell …`")],
    exercises=["Extend the core-API snippet to create 10 cubes in a row with **one** `Cube(...)` call "
               "(pass a list of paths and positions).",
               "Turn `m4_snippet_core_api.py` into a standalone script that prints the cube height every 10 frames.",
               "Read `standalone_examples/api/isaacsim.core.experimental.api/add_cubes.py` and explain "
               "`RigidPrim.set_velocities`."],
    quiz=[("What must be the first Isaac Sim import in a standalone script?", "`from isaacsim import SimulationApp`, then create it."),
          ("4.x `DynamicCuboid` in 6.1?", "`Cube` + `RigidPrim` + `GeomPrim(apply_collision_apis=True)`."),
          ("Which layer's code survived 4.2 → 6.1 unchanged?", "Raw OpenUSD (`pxr`) code.")],
)

L["module4_sil/lesson3_isaac_ros_segmentation.md"] = dict(
    video="4.3_isaac_ros_segmentation",
    diagrams=[("m4-sil-segmentation", "Software-in-the-loop with Isaac ROS")],
    time="1–2 h (mostly Isaac ROS setup)",
    learn=["Publish simulated camera images to ROS 2", "Connect Isaac Sim to an Isaac ROS container"],
    concepts="""
**Camera graphs.** A camera publisher needs a *render product* (the camera rendered at a resolution); the
*ROS 2 Camera* tool creates it plus the publisher nodes for RGB, depth, segmentation or boxes.

**Containers and distros.** Isaac ROS runs in Docker, often on Humble. DDS lets Humble and Jazzy exchange
standard messages if RMW and domain ID match; when in doubt, run Isaac Sim with the same distro.
""",
    checks=[("`ros2 topic hz /rgb`", "a steady rate while playing"),
            ("`rqt_image_view /rgb`", "the Hawk camera image")],
    exercises=["Also publish `depth` and view it in RViz as an Image display.",
               "Lower the camera resolution in the dialog and compare `/rgb` rates."],
    quiz=[("What does a camera publisher need besides the camera prim?", "A render product."),
          ("Isaac ROS on Humble, Isaac Sim on Jazzy, no messages — one fix?",
           "Launch Isaac Sim with `ROS_DISTRO=humble` (bundled) and matching RMW/domain.")],
)

L["module5_hil/README.md"] = dict(
    video="5_hardware_in_the_loop",
    diagrams=[("m5-hil", "Hardware-in-the-loop deployment")],
    time="reading 15 min (hands-on needs a Jetson)",
    learn=["Explain hardware-in-the-loop (HIL)", "Prepare the Isaac Sim side for a Jetson"],
    concepts="""
**HIL vs SIL.** In SIL the robot software runs on your workstation; in HIL it runs on the robot's real
computer (Jetson), so you also test its timing, GPU load and networking — without risking the robot.

**Simulated time.** The simulator may run slower or faster than real time. Publishing `/clock` and
setting `use_sim_time: true` on the Jetson keeps every node on the simulator's clock.
""",
    checks=[("On the Jetson: `ros2 topic list`", "Isaac Sim's topics (clock, scan, rgb)"),
            ("On the Jetson: `ros2 topic hz /clock`", "steady rate while Isaac Sim plays")],
    exercises=["Without a Jetson: run the 'Jetson side' in a second terminal (or Docker) on the same PC with "
               "`use_sim_time:=true` and check it follows `/clock`."],
    quiz=[("What does `use_sim_time: true` do?", "Nodes use the /clock topic instead of the wall clock."),
          ("Two settings that must match on both machines?", "ROS_DOMAIN_ID and the RMW implementation.")],
)


def top_block(rel, d):
    depth = rel.count("/")
    up = "../" * depth
    lines = ["<!-- tutorial:start -->", "",
             f"> 🎬 **Video walkthrough:** [`{d['video']}.mp4`]({up}videos/{d['video']}.mp4) "
             f"(captions burned in; text: [`.srt`]({up}videos/subtitles/{d["video"]}.srt)) · ⏱ **Time:** {d['time']}", "",
             "**You will learn to**", ""]
    lines += [f"- {x}" for x in d["learn"]]
    lines.append("")
    for slug, cap in d["diagrams"]:
        lines += [f"![{cap}]({up}diagrams/{slug}.png)",
                  f"*{cap} — [interactive HTML]({up}diagrams/{slug}.html)*", ""]
    lines += ["## Concepts", d["concepts"].strip(), "", "<!-- tutorial:end -->"]
    return "\n".join(lines)


def bottom_block(d):
    lines = ["<!-- practice:start -->", "", "## Check your result", "", "| Do this | You should see |", "|---|---|"]
    lines += [f"| {a} | {b} |" for a, b in d["checks"]]
    lines += ["", "## Exercises", ""]
    lines += [f"{i}. {x}" for i, x in enumerate(d["exercises"], 1)]
    lines += ["", "## Quiz", ""]
    for i, (q, a) in enumerate(d["quiz"], 1):
        lines += [f"{i}. {q}", f"   <details><summary>Answer</summary>{a}</details>", ""]
    lines.append("<!-- practice:end -->")
    return "\n".join(lines)


def apply(rel, d):
    path = os.path.join(ROOT, rel)
    s = open(path).read()
    s = re.sub(r"\n?<!-- tutorial:start -->.*?<!-- tutorial:end -->\n?", "\n", s, flags=re.S)
    s = re.sub(r"\n?<!-- practice:start -->.*?<!-- practice:end -->\n?", "\n", s, flags=re.S)
    # insert the top block after the first '---' rule (end of the lesson header), else after the H1 paragraph
    top = top_block(rel, d)
    if "\n---\n" in s:
        i = s.index("\n---\n")
        s = s[:i] + "\n\n" + top + "\n" + s[i:]
    else:
        i = s.index("\n\n", s.index("\n# ") if s.startswith("\n") else 0)
        s = s[:i] + "\n\n" + top + "\n" + s[i:]
    s = s.rstrip() + "\n\n" + bottom_block(d) + "\n"
    with open(path, "w") as f:
        f.write(s)
    print("updated", rel)


if __name__ == "__main__":
    for rel, d in L.items():
        apply(rel, d)
