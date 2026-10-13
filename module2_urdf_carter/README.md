# Module 2 — Ingesting Robot Assets (project)

**Project goal:** take a robot that only exists as a URDF file (Carter), turn it into a drivable,
sensor-equipped Isaac Sim robot — then compare it with NVIDIA's production Nova Carter.

| # | Lesson | Video | Diagram(s) | Checkpoint |
|---|---|---|---|---|
| 2.1 | [Importing URDF](lesson1_importing_urdf.md) | [▶ 2.1](../videos/2.1_importing_urdf.mp4) | [pipeline](../diagrams/m2-urdf-pipeline.png) · [asset structure](../diagrams/m2-carter-structure.png) | `m2_import_carter.py` |
| 2.2 | [Preparing the simulation](lesson2_preparing_the_simulation.md) | [▶ 2.2](../videos/2.2_preparing_the_simulation.mp4) | [controller numbers](../diagrams/m2-carter-drive.png) | `m2_import_carter.py` |
| 2.3 | [Adding sensors](lesson3_adding_sensors.md) | [▶ 2.3](../videos/2.3_adding_sensors.mp4) | [sensor layout](../diagrams/m2-carter-sensors.png) | — |
| 2.4 | [Nova Carter](lesson4_nova_carter.md) | [▶ 2.4](../videos/2.4_nova_carter.mp4) | [sensor suite](../diagrams/m2-nova-carter.png) | — |

## Project milestones

- [ ] `carter.usda` imported, **physx** variant selected, wheel drives set (2.1)
- [ ] Carter in a Flat Grid scene, driven with W A S D, ≤ 0.5 m/s (2.2) — `m2_import_carter.py --headless --test` passes
- [ ] RGB_Sensor + RTX lidar on `chassis_link`, obstacles detected (2.3)
- [ ] Nova Carter loaded and its sensors identified (2.4)

**Stretch project:** import a different URDF (e.g. `exts/isaacsim.robot_motion.cumotion/robot_configurations/ur10/robot.urdf`
with *Base Type = Fixed*) and move one joint with a position drive.

## Choose where to go next

Compare one joint and one sensor on your imported Carter with Nova Carter. Describe which settings
you had to supply yourself and which arrived with the prepared asset.

For perception data, continue to [Module 3](../module3_sdg/README.md). To drive the prepared robot
from ROS 2 and explore Python scripting, continue to [Module 4](../module4_sil/README.md).
