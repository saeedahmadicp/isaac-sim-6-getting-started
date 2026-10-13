# Module 4 — Developing Robots With Software-in-the-Loop (project)

**Project goal:** drive Nova Carter from ROS 2 (`/cmd_vel`), script scenes in Python, and stream its camera
to an Isaac ROS pipeline.

| # | Lesson | Video | Diagram | Checkpoint |
|---|---|---|---|---|
| 4.1 | [OmniGraph + /cmd_vel](lesson1_omnigraph_cmd_vel.md) | [▶ 4.1](../videos/4.1_omnigraph_cmd_vel.mp4) | [control loop](../diagrams/m4-cmd-vel.png) | `m4_nova_carter_cmd_vel.py` |
| 4.2 | [Python scripting](lesson2_python_scripting.md) | [▶ 4.2](../videos/4.2_python_scripting.mp4) | [API layers](../diagrams/m4-python-layers.png) | `m4_run_snippet.py` + snippets |
| 4.3 | [Camera images for Isaac ROS](lesson3_isaac_ros_segmentation.md) | [▶ 4.3](../videos/4.3_isaac_ros_segmentation.mp4) | [SIL setup](../diagrams/m4-sil-segmentation.png) | — |

The concept lessons (*Intelligent Robots*, *Software-in-the-Loop*, *Foundations of Image Segmentation*) are
version-independent — read them on the course site.

## Project milestones

- [ ] `ros2 topic pub /cmd_vel …` and `teleop_twist_keyboard` drive Nova Carter (4.1) — checkpoint passes
- [ ] Both Script Editor snippets run; the core-API one is in your own words (4.2)
- [ ] `/rgb` from the Hawk camera visible in `rqt_image_view` (4.3)

**Stretch project:** combine 4.1 and 1.4 — write an rclpy node that reads `/scan` from Nova Carter's front
RPLidar and publishes `/cmd_vel` to stop before obstacles.

## Optional capstone brief: stop before an obstacle

Combine the lidar and velocity-command lessons into one behavior. Start by identifying the actual
scan topic on your scene and checking its frame and forward direction. Write a ROS 2 node that reads
valid forward ranges and commands a stop below a distance you choose.

Work through three milestones:

1. Print the forward distance while the robot stays still. Compare it with a known obstacle placement.
2. Publish zero velocity when the obstacle is too close, or when the scan is missing or stale.
3. Test slow forward motion toward an obstacle and show the resulting stop. Repeat from another
   starting distance and record the smallest clearance.

**Done means:** you can show a scan, a command, and the resulting motion; explain your threshold; and
reproduce the stop. This is an extension brief, not an implemented or validated collision-avoidance
controller. The course checkpoint only tests following velocity commands.

[Module 5](../module5_hil/README.md) explores moving the robot-software side onto a Jetson.
