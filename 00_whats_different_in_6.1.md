# What's different: course (4.2 / 4.5) → Isaac Sim 6.1

The menu paths below come from the 6.1 menu source code in this install (`exts/isaacsim.gui.menu`,
`exts/*/ui`) and the module names from `exts/` and `extsDeprecated/`.

## 1. Launching

| Course | 6.1 |
|---|---|
| `./isaac-sim.selector.sh` → untick ROS bridge → Start | `./isaac-sim.sh` (the selector is gone) |
| Source `/opt/ros/humble/setup.bash` **before** launching | Not needed: `isaac-sim.sh` sources `setup_ros_env.sh`, which loads the **bundled Jazzy** libs (`ROS_DISTRO=jazzy`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`) |
| "Make sure the ROS bridge is not enabled" | Leave it enabled. It loads at startup and does nothing until a ROS graph plays |

## 2. Menus

| What | 4.2 | 4.5 | **6.1** |
|---|---|---|---|
| Differential Controller graph | Isaac Utils > Common Omnigraphs | Tools > Robotics > OmniGraph Controllers | **Tools > Robotics > OmniGraph Controllers > Differential Controller** (unchanged from 4.5) |
| ROS 2 graph shortcuts | Isaac Utils > ROS2 OmniGraphs | Tools > Robotics > ROS 2 OmniGraphs | **Tools > Robotics > ROS 2 OmniGraphs > Camera / RTX Lidar / RTX Radar / TF Publisher / …** |
| Flat grid | Create > Isaac > Environments > Flat Grid | Create > Environments > Flat Grid | **Create > Environments > Flat Grid** (also *Black Grid*, *Simple Room*) |
| Nova Carter | Create > Isaac > Robots > … | Create > Robots > Nova Carter with Sensors | **Create > Robots > Nova Carter with Sensors** |
| Asset browser | Content > NVIDIA/Assets/Isaac/4.2 | Isaac Sim Assets [Beta] | **Window > Browsers > Isaac Sim Assets** (or *Asset Browser* at the bottom of Create > Robots / Environments / Sensors) |
| PhysX Lidar | Create > Isaac > Sensors > PhysX Lidar > Rotating | Create > Sensors > PhysX Lidar > Rotating | still at **Create > Sensors > PhysX Lidar > Rotating**, but **deprecated** |
| RTX Lidar | Create > Isaac > Sensors > RTX Lidar | Create > Sensors > RTX Lidar | **Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D** (2D) / *Example Rotary* (3D) / vendor models |
| 2nd viewport | Window > Viewport > Viewport 2 | Window > Viewports | **Window > Viewports > Viewport 2** |
| URDF importer | Isaac Utils > Workflows > URDF Importer | File > Import | **File > Import** (new options panel, see §4) |
| Semantics editor | Window > Extensions | Tools > Replicator > Semantics Schema Editor | **Tools > Replicator > Semantics Schema Editor** |
| Script editor | Window > Script Editor | same | **Window > Script Editor** |

Unchanged from the course: *Create > Mesh > Cube/Cylinder*, *Create > Physics > Physics Scene / Ground
Plane / Joint > Revolute Joint*, right-click *Add > Physics > Rigid Body with Colliders Preset*,
*Add > Physics > Angular Drive*, *Add > Physics > Articulation Root*, *Create > Camera*,
*Create > Visual Scripting > Action Graph*.

## 3. Sensors

| Course | 6.1 | Why |
|---|---|---|
| PhysX Lidar + `Isaac Read Lidar Beams` → `ROS2 Publish Laser Scan` | **RTX Lidar `Example_Rotary_2D`** + *Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar* (tick *Laser Scan*) | `isaacsim.sensors.physx` moved to `extsDeprecated/`. It still loads in 6.1, but new work should use RTX sensors |
| Lidar "Draw Lines / Draw Points" in Raw USD Properties | RTX lidar: attach the `draw-point-cloud` writer, or check the point cloud in RViz | RTX lidars are rendered with ray tracing, not PhysX raycasts |
| Obstacles need *Rigid Body with Colliders* to block the PhysX lidar | RTX lidar sees **any rendered geometry**, colliders not required (keep them for physics) | ray-traced |
| `omni.isaac.sensor` / `isaacsim.sensors.camera.Camera` | `isaacsim.sensors.experimental.rtx` (`RtxCamera`, `Lidar`, `LidarSensor`) | new API |

## 4. URDF importer (File > Import → .urdf)

| 4.5 options | 6.1 options |
|---|---|
| Links: *Static / Moveable base* | **Options > Base Type: Source / Fixed / Mobile** → choose **Mobile** |
| Joints and Drives: *Natural Frequency*, per-joint target type (Velocity / None) | **Not in the dialog.** Set drives after import in the joint's Property panel (lesson 2.1) |
| Output: one USD | **A folder** `carter/carter.usda` + `payloads/` with a **Physics variant set** (`physx`, `mujoco`, `physics`, `none`). **Select `physx`** or the robot has no physics |
| Joints under `chassis_link` (4.2) or a `joints` folder (4.5) | Joints under **`/carter/Physics/`**, links under **`/carter/Geometry/`** |
| Imported into the open stage | By default it **opens the converted robot as a new stage**. Tick **Add Reference to Stage** to drop it into your current scene |
| — | Writes the USD **next to the .urdf** unless you set *Model > USD Output* |

## 5. Python API

| Course (4.2/4.5) | 6.1 |
|---|---|
| `from omni.isaac.kit import SimulationApp` | `from isaacsim import SimulationApp` |
| `omni.isaac.core.objects.DynamicCuboid` | `isaacsim.core.experimental.objects.Cube` + `prims.RigidPrim` + `prims.GeomPrim(apply_collision_apis=True)` |
| `omni.isaac.core.objects.ground_plane.GroundPlane` | `isaacsim.core.experimental.objects.GroundPlane` |
| `omni.isaac.core.physics_context.PhysicsContext()` | `UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")` (or `isaacsim.core.simulation_manager`) |
| `omni.isaac.core.utils.nucleus.get_assets_root_path` | `isaacsim.storage.native.get_assets_root_path` |
| `omni.isaac.core.utils.stage.open_stage` | `omni.usd.get_context().open_stage(url)` or `isaacsim.core.experimental.utils.stage` |
| `pxr.Semantics.SemanticsAPI` | `UsdSemantics.LabelsAPI`, or `rep.functional.modify.semantics(...)` |
| `isaacsim.core.api.World` (5.x) | deprecated in 6.x (`extsDeprecated/isaacsim.core.api`) |
| Raw `pxr` USD / `UsdPhysics` / `PhysxSchema` code | **unchanged**, still works |

`omni.isaac.*` names were renamed to `isaacsim.*` in 4.5 and removed later. Saved Action Graphs with old
node types are auto-migrated by `isaacsim.core.deprecation_manager` when you open them.

## 6. OmniGraph node types used in the course

| Node (UI name) | 6.1 type id |
|---|---|
| On Playback Tick | `omni.graph.action.OnPlaybackTick` |
| Differential Controller | `isaacsim.robot.wheeled_robots.DifferentialController` |
| Articulation Controller | `isaacsim.core.nodes.IsaacArticulationController` |
| ROS2 Context | `isaacsim.ros2.bridge.ROS2Context` |
| ROS2 Subscribe Twist | `isaacsim.ros2.bridge.ROS2SubscribeTwist` |
| ROS2 Publish Laser Scan | `isaacsim.ros2.bridge.ROS2PublishLaserScan` |
| ROS2 RTX Lidar Helper | `isaacsim.ros2.bridge.ROS2RtxLidarHelper` |
| Isaac Read Simulation Time | `isaacsim.core.nodes.IsaacReadSimulationTime` |
| Isaac Read Lidar Beams (PhysX, deprecated) | `isaacsim.sensors.physx.IsaacReadLidarBeams` |
| Scale To/From Stage Units | `isaacsim.core.nodes.OgnIsaacScaleToFromStageUnit` |
| Break 3-Vector | `omni.graph.nodes.BreakVector3` |
| Keyboard (Differential Controller tool) | `omni.graph.nodes.ReadKeyboardState` |

## 7. Physics

* 6.1 also ships the **Newton** physics engine (`./isaac-sim.newton.sh`, `isaacsim.physics.newton`). The
  course and these lessons use **PhysX** (the default `./isaac-sim.sh`).
* Units are unchanged: angular drive *Target Velocity* is in **deg/s**, damping in N·m·s/deg.

## 8. Known pitfalls in Isaac Sim 6.1

Each one came up while writing the checkpoint scripts. The lessons already work around them.

| Symptom | Cause / fix | Lesson |
|---|---|---|
| RTX lidar's ROS topic exists but **no messages arrive** | The lidar was on a separate rigid body fixed-jointed to the chassis (the course's *Front_Sensor* pattern). Put the RTX lidar **directly under the chassis body**, as Nova Carter does | 1.3 |
| 2D scan shows a close "obstacle" behind the robot | Lidar below the wheel tops sees the robot itself. Raise it | 1.3 |
| Imported URDF robot doesn't move or fall | **Physics variant** not selected. Set *Variants > Physics = physx* | 2.1 |
| Imported URDF wheels don't drive | 6.1 importer leaves drive gains at 0. Set damping on the wheel joints | 2.1 |
| Replicator: every frame identical | Graph randomizers (`rep.trigger.on_frame`) fired only on the first `rep.orchestrator.step()`. Use the functional API in a Python loop, or `on_frame(max_execs=N)` + `rep.orchestrator.run_until_complete()` | 3 |
| Replicator: script hangs while building the randomization graph | `rep.create.material_omnipbr` + `rep.randomizer.materials` inside a trigger. Use `rep.functional.create_batch.material` + `rep.functional.modify.attribute` | 3 |
| KITTI labels contain warehouse classes | Referenced `SemanticsAPI` labels can't be removed with `RemoveProperty`. Block them (`attr.Block()`), and filter rows (`semantic_filter_predicate` isn't applied by the fast bbox annotators) | 3 |
| Script-created obstacle stays at the origin | `UsdGeom.XformCommonAPI.SetTranslate` silently fails on *Create > Mesh* prims (they have an orient op). Set `xformOp:translate` directly | 1.3 |
| Standalone script crashes on its first `update()` after enabling the ROS 2 bridge | Call `simulation_app.update()` right after enabling `isaacsim.ros2.bridge`, **before** opening or creating a stage | 1.4, 4.1 |
| Custom rclpy subscriber gets no lidar/camera data | Sensor topics are best-effort. Subscribe with `rclpy.qos.qos_profile_sensor_data` | 1.4 |
| Standalone RTX sensor scripts | Start the app with `SimulationApp({..., "enable_motion_bvh": True})` (what the 6.1 examples do) | 1.4 |
