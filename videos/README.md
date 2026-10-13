# Video tutorials

One narrated video per lesson (1920×1080, H.264/AAC). Animated slides — each lesson's steps revealed in
sync with the narration, the course diagrams, a slow push-in and crossfades — with **small burned-in captions**.
Narration: ElevenLabs, voice *Matilda*, model `eleven_multilingual_v2`. Caption text: [`subtitles/`](subtitles/).

> These are explainer videos made from slides and diagrams, not screen recordings of Isaac Sim.

| Video | Length | Lesson |
|---|---|---|
| [▶ Course introduction](00_course_intro.mp4) | 1:48 | [README.md](../README.md) |
| [▶ Lesson 1.1 — Building a simple robot](1.1_building_a_simple_robot.mp4) | 2:33 | [module1_first_robot/lesson1_building_a_simple_robot.md](../module1_first_robot/lesson1_building_a_simple_robot.md) |
| [▶ Lesson 1.2 — Controlling the robot](1.2_controlling_the_robot.mp4) | 1:49 | [module1_first_robot/lesson2_controlling_the_robot.md](../module1_first_robot/lesson2_controlling_the_robot.md) |
| [▶ Lesson 1.3 — Adding sensors](1.3_adding_sensors.mp4) | 1:57 | [module1_first_robot/lesson3_adding_sensors.md](../module1_first_robot/lesson3_adding_sensors.md) |
| [▶ Lesson 1.4 — Lidar to ROS 2 and RViz](1.4_ros2_and_rviz.mp4) | 2:09 | [module1_first_robot/lesson4_ros2_and_rviz.md](../module1_first_robot/lesson4_ros2_and_rviz.md) |
| [▶ Lesson 2.1 — Importing URDF assets](2.1_importing_urdf.mp4) | 1:39 | [module2_urdf_carter/lesson1_importing_urdf.md](../module2_urdf_carter/lesson1_importing_urdf.md) |
| [▶ Lesson 2.2 — Preparing the simulation](2.2_preparing_the_simulation.mp4) | 1:34 | [module2_urdf_carter/lesson2_preparing_the_simulation.md](../module2_urdf_carter/lesson2_preparing_the_simulation.md) |
| [▶ Lesson 2.3 — Adding sensors to Carter](2.3_adding_sensors.mp4) | 1:22 | [module2_urdf_carter/lesson3_adding_sensors.md](../module2_urdf_carter/lesson3_adding_sensors.md) |
| [▶ Lesson 2.4 — Nova Carter](2.4_nova_carter.mp4) | 1:13 | [module2_urdf_carter/lesson4_nova_carter.md](../module2_urdf_carter/lesson4_nova_carter.md) |
| [▶ Module 3 — Synthetic data with Replicator](3.1_synthetic_data.mp4) | 1:55 | [module3_sdg/lesson1_generate_dataset.md](../module3_sdg/lesson1_generate_dataset.md) |
| [▶ Lesson 4.1 — Driving from ROS 2](4.1_omnigraph_cmd_vel.mp4) | 1:35 | [module4_sil/lesson1_omnigraph_cmd_vel.md](../module4_sil/lesson1_omnigraph_cmd_vel.md) |
| [▶ Lesson 4.2 — Python scripting](4.2_python_scripting.mp4) | 1:35 | [module4_sil/lesson2_python_scripting.md](../module4_sil/lesson2_python_scripting.md) |
| [▶ Lesson 4.3 — Isaac ROS segmentation](4.3_isaac_ros_segmentation.mp4) | 1:13 | [module4_sil/lesson3_isaac_ros_segmentation.md](../module4_sil/lesson3_isaac_ros_segmentation.md) |
| [▶ Module 5 — Hardware-in-the-loop](5_hardware_in_the_loop.mp4) | 0:59 | [module5_hil/README.md](../module5_hil/README.md) |

Total: 23 min 26 s.

## Rebuilding

Everything is generated from `_build/content.py` (slide text + narration script):

```bash
python3 learning_resource/videos/_build/make_slides.py [lesson_id]   # slide frames + narration text -> _work/<id>/
# narration: one ElevenLabs text_to_speech call per _work/<id>/sNN.txt, saved into _work/<id>/sNN_audio/
python3 learning_resource/videos/_build/assemble.py [lesson_id]      # -> <id>.mp4 + subtitles/<id>.srt
```

`_work/` keeps the narration mp3s (paid ElevenLabs output — don't delete them) and cached per-slide clips, so
changing captions or timing only re-runs the cheap final pass. Caption look is the `style` string in `assemble.py`.
