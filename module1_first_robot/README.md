# Module 1 — Building Your First Robot (project)

![Course map](../diagrams/course-map.png)

**Project goal:** a four-wheeled robot you built from primitives, driven with the keyboard, whose 2D lidar
streams to ROS 2 and shows up in RViz.

| # | Lesson | Video | Diagram(s) | Checkpoint |
|---|---|---|---|---|
| 1.1 | [Building a simple robot](lesson1_building_a_simple_robot.md) | [▶ 1.1](../videos/1.1_building_a_simple_robot.mp4) | [ladder](../diagrams/m1-build-ladder.png) · [structure](../diagrams/m1-robot-structure.png) | `m1_build_simple_robot.py` |
| 1.2 | [Controlling the robot](lesson2_controlling_the_robot.md) | [▶ 1.2](../videos/1.2_controlling_the_robot.mp4) | [controller graph](../diagrams/m1-diff-controller.png) | (graph built by the menu tool) |
| 1.3 | [Adding sensors](lesson3_adding_sensors.md) | [▶ 1.3](../videos/1.3_adding_sensors.mp4) | [sensor mounting](../diagrams/m1-sensor-mount.png) | `m1_ros2_lidar.py` |
| 1.4 | [ROS 2 + RViz](lesson4_ros2_and_rviz.md) | [▶ 1.4](../videos/1.4_ros2_and_rviz.mp4) | [data path](../diagrams/m1-ros2-lidar.png) | `m1_ros2_lidar.py` |

## Project milestones

- [ ] The robot drives straight on fixed drives (1.1) — `m1_build_simple_robot.py --headless --test` passes
- [ ] W A S D drives and turns it (1.2)
- [ ] Robot_Camera view follows the robot; RTX lidar sits on the chassis above the wheels (1.3)
- [ ] `ros2 topic hz /scan_lidar` ≈ 10 Hz and RViz shows the obstacles (1.4) — `m1_ros2_lidar.py --headless --test` passes

**Stretch project:** add a 3D lidar (Ouster OS1) and a second camera looking backwards, publish both, and
build an RViz config that shows the robot's surroundings while you drive.

## Take it beyond the checklist

Drive toward an obstacle, then turn so the lidar sees a different part of the scene. Explain how the
camera image and the scan represent the same surroundings differently. Save your scene and one
observation you can reproduce.

Next, [import Carter in Module 2](../module2_urdf_carter/README.md). You will reuse what you learned
about bodies, joints, and drives while letting an importer construct the robot.
