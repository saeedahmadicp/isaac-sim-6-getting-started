"""Video scripts: one entry per lesson. Slide text is what is shown; `say` is what the narrator reads.

Slide types
  title   : eyebrow, title, sub
  diagram : title, img (diagram slug in learning_resource/diagrams), caption
  steps   : title, bullets [(text, chip|None)], say = [intro, one line per bullet]
  callout : kind (trap|tip), title, body, code
"""

LESSONS = {}


def lesson(lid, title, slides):
    LESSONS[lid] = {"title": title, "slides": slides}


# ============================================================================ course intro
lesson("00_course_intro", "Course introduction", [
    {"type": "title", "eyebrow": "Getting Started With Isaac Sim · 6.1 edition", "title": "Course introduction",
     "sub": "NVIDIA's robotics learning path, rewritten for Isaac Sim 6.1",
     "say": "Welcome. This course is NVIDIA's Getting Started With Isaac Sim learning path, rewritten step by step "
            "for Isaac Sim six point one. The original course was written for "
            "version four point five, so many menus, sensors and Python imports have changed. Every change is marked in "
            "the lessons, and every lesson comes with a checkpoint script you can run yourself."},
    {"type": "diagram", "title": "Five modules, one robot story", "img": "course-map",
     "caption": "Start with Module 1 — every later module builds on it",
     "say": "The course has five modules. In module one you build a small robot from scratch and stream its lidar to "
            "ROS 2. Module two imports a real robot, Carter, from a URDF file. Module three generates a synthetic "
            "dataset with Replicator. Module four closes the loop with ROS 2 software in the loop, and module five "
            "explains how the same setup connects to a Jetson for hardware in the loop."},
    {"type": "steps", "title": "How to study each lesson", "bullets": [
        ("Read the lesson Markdown file", "learning_resource/moduleN_*/lessonX.md"),
        ("Follow the steps in the GUI", "./isaac-sim.sh"),
        ("Stuck? Run the checkpoint script", "./python.sh learning_resource/scripts/m1_*.py"),
        ("Self-check without a window", "--headless --test"),
    ], "say": [
        "Here is the routine for every lesson.",
        "First, read the lesson file. It keeps the course structure and marks every six point one change.",
        "Then do the steps yourself in the Isaac Sim window. You learn the interface by clicking through it.",
        "If you get stuck, run the matching checkpoint script. It builds the finished result, so you can compare.",
        "And every script has a headless test mode that prints pass or fail, which is handy after an upgrade.",
    ]},
    {"type": "callout", "kind": "tip", "title": "What changed most since 4.5",
     "body": "RTX lidar replaces the PhysX lidar · the URDF importer was rewritten · ROS 2 Jazzy is bundled · "
             "omni.isaac.core is gone", "code": "learning_resource/00_whats_different_in_6.1.md",
     "say": "Four changes matter most. The RTX lidar replaces the old PhysX lidar. The URDF importer was rewritten and "
            "now needs two extra steps. ROS 2 Jazzy libraries ship inside Isaac Sim, so you no longer source ROS before "
            "launching. And the old omni dot isaac dot core Python module is gone. The cheat sheet file lists all of "
            "this. Let's start with module one."},
])

# ============================================================================ 1.1
lesson("1.1_building_a_simple_robot", "Lesson 1.1 — Building a simple robot", [
    {"type": "title", "eyebrow": "Module 1 · Lesson 1.1", "title": "Building a simple robot",
     "sub": "From a cube and four cylinders to a robot that drives",
     "say": "In this lesson you build a four wheeled robot out of plain shapes: a cube for the body and four "
            "cylinders for the wheels. Then you add physics, joints and motors until it drives forward on its own."},
    {"type": "diagram", "title": "The six-step ladder", "img": "m1-build-ladder",
     "caption": "Press Play after every step",
     "say": "The lesson climbs six steps. Meshes are only visuals. A physics scene adds gravity and a ground. Rigid "
            "bodies with colliders make the shapes fall and collide. Revolute joints hold the wheels on. Angular drives "
            "spin the rear wheels, and an articulation root ties everything into one robot. Press play after each step "
            "and watch what physics adds."},
    {"type": "steps", "title": "Launch and add physics", "bullets": [
        ("Launch Isaac Sim (no selector in 6.1)", "./isaac-sim.sh"),
        ("Add a cube", "Create > Mesh > Cube"),
        ("Add gravity and a floor", "Create > Physics > Physics Scene · Ground Plane"),
        ("Make it a physical object", "Add > Physics > Rigid Body with Colliders Preset"),
    ], "say": [
        "Let's start.",
        "Launch Isaac Sim with the isaac sim dot s h script. Version six point one has no selector window anymore.",
        "Create a cube from the Create, Mesh menu. Press play: nothing happens, it is only a visual mesh.",
        "Add a physics scene and a ground plane from the Create, Physics menu.",
        "Then right click the cube and add a rigid body with colliders. Now it falls and lands on the ground.",
    ]},
    {"type": "diagram", "title": "SimpleRobot, seen from above", "img": "m1-robot-structure",
     "caption": "Cube = body 0 · each wheel = body 1 of its revolute joint",
     "say": "Here is the robot from above. Scale the cube to two by one by half a meter and put it inside an Xform "
            "called SimpleRobot. Add four cylinders, rotated ninety degrees about X and scaled to zero point seven five, "
            "and place them at plus and minus half a meter forward and plus and minus zero point seven five to the side. "
            "Each wheel gets a revolute joint, with the cube as body zero and the wheel as body one."},
    {"type": "steps", "title": "Joints and drives", "bullets": [
        ("Select Cube, then Ctrl+click a wheel", "Create > Physics > Joint > Revolute Joint"),
        ("Axis Y · Local Rotation 1", "(-90, 0, 0)"),
        ("Lift the robot onto the ground", "SimpleRobot Translate Z = 0.375"),
        ("Rear joints: Angular Drive", "damping 10000 · target 50 °/s"),
    ], "say": [
        "Now the joints.",
        "Select the cube first, then control click a wheel, and create a revolute joint. The selection order sets body zero and body one.",
        "Set the axis to Y and local rotation one to minus ninety, zero, zero, so both joint frames line up.",
        "Lift the whole robot by zero point three seven five meters, the wheel radius, so the wheels rest on the ground.",
        "Finally add an angular drive to the two rear joints, with damping ten thousand and a target of fifty degrees per second. Press play, and the robot drives forward.",
    ]},
    {"type": "callout", "kind": "tip", "title": "Checkpoint", "body":
        "The script builds the same robot and checks that it drove forward (0.96 m in 3 s).",
     "code": "./python.sh learning_resource/scripts/m1_build_simple_robot.py --headless --test",
     "say": "To check your work, run the m1 build simple robot checkpoint script. It builds exactly this robot, "
            "drives it for three seconds and checks that it moved about one meter forward. You can also save its stage "
            "and open it next to yours. In the next lesson you will steer it with the keyboard."},
])

# ============================================================================ 1.2
lesson("1.2_controlling_the_robot", "Lesson 1.2 — Controlling the robot", [
    {"type": "title", "eyebrow": "Module 1 · Lesson 1.2", "title": "Controlling the robot",
     "sub": "A Differential Controller graph, then W A S D",
     "say": "Fixed motor speeds only drive straight. In this lesson you replace them with a differential controller, "
            "first set by hand and then driven from the keyboard."},
    {"type": "diagram", "title": "The controller graph", "img": "m1-diff-controller",
     "caption": "Built for you by Tools > Robotics > OmniGraph Controllers",
     "say": "This is the action graph you will create. Every frame, the playback tick runs the differential "
            "controller. It turns a forward speed and a turning speed into one speed per wheel, using the wheel radius "
            "and the distance between the wheels. The articulation controller then applies those speeds to the rear "
            "joints named in the array node."},
    {"type": "steps", "title": "Create the controller", "bullets": [
        ("Give the robot an articulation root", "SimpleRobot > Add > Physics > Articulation Root"),
        ("Open the tool", "Tools > Robotics > OmniGraph Controllers > Differential Controller"),
        ("Wheel radius · distance between wheels", "0.375 · 1.5"),
        ("Joint names", "Rear_Left_Joint · Rear_Right_Joint"),
    ], "say": [
        "Here are the steps.",
        "First add an articulation root to SimpleRobot. The controller finds the joints through it.",
        "Open Tools, Robotics, OmniGraph Controllers, Differential Controller. The path is the same as in four point five.",
        "Enter a wheel radius of zero point three seven five and a distance between wheels of one point five.",
        "Type the two rear joint names, pick SimpleRobot as the robot prim, and click OK.",
    ]},
    {"type": "steps", "title": "Drive it", "bullets": [
        ("Play, then set Linear Velocity on the node", "1 = forward · -1 = back"),
        ("Delete the graph, rebuild with keyboard", "Use Keyboard Control (WASD) ✓"),
        ("Click the viewport, drive", "W A S D"),
        ("Tune speed", "ScaleLinear · ScaleAngular"),
    ], "say": [
        "Now drive it.",
        "Press play. The robot stays still until you set the linear velocity on the controller node. Try one, then minus one.",
        "Then delete the graph and create it again with the keyboard option ticked.",
        "Click inside the viewport so it has keyboard focus, and drive with W, A, S and D.",
        "If it is too fast or too slow, change the two constant nodes named scale linear and scale angular.",
    ]},
    {"type": "callout", "kind": "trap", "title": "Common mistakes", "body":
        "No articulation root → controller does nothing · old drive targets still at 50 → robot wanders · "
        "left/right swapped → it turns instead of going straight", "code": None,
     "say": "Three mistakes are common. Without an articulation root, the controller silently does nothing. If the old "
            "drive targets are still fifty degrees per second, the robot wanders on its own, so set them to zero. And "
            "if the left and right names are swapped, it turns when you ask it to go straight."},
])

# ============================================================================ 1.3
lesson("1.3_adding_sensors", "Lesson 1.3 — Adding sensors", [
    {"type": "title", "eyebrow": "Module 1 · Lesson 1.3", "title": "Adding sensors",
     "sub": "An RGB camera and a 2D lidar — the 6.1 way",
     "say": "Now the robot gets eyes: an RGB camera and a two dimensional lidar. This is the lesson where Isaac Sim six "
            "point one differs most from the course, so watch for the warning."},
    {"type": "steps", "title": "The camera", "bullets": [
        ("Front_Sensor Xform + Rigid Body + Fixed Joint to Cube", "Create > Physics > Joint > Fixed Joint"),
        ("Camera on the mount", "Create > Camera · Rotate Y = -90"),
        ("Look through it", "Viewport camera menu > Cameras > Robot_Camera"),
        ("Two views at once", "Window > Viewports > Viewport 2"),
    ], "say": [
        "The camera follows the course.",
        "Create an Xform called Front Sensor at the front of the robot, make it a rigid body, and fix it to the cube with a fixed joint.",
        "Add a camera under the mount and rotate it minus ninety degrees about Y so it looks forward.",
        "Use the camera menu at the top of the viewport to look through it.",
        "And open a second viewport from Window, Viewports, so you can watch the scene and the robot's view together.",
    ]},
    {"type": "diagram", "title": "Where each sensor goes in 6.1", "img": "m1-sensor-mount",
     "caption": "RTX lidar on a fixed-jointed body publishes nothing",
     "say": "The lidar is different. The course used a PhysX lidar, which is deprecated in six point one. Its "
            "replacement is the RTX lidar. While testing this lesson we found a trap: an RTX lidar placed on the fixed "
            "jointed sensor body produces no data at all, with no error. Placed directly under the chassis body it "
            "works, which is also how NVIDIA's own Nova Carter is built."},
    {"type": "steps", "title": "The RTX lidar", "bullets": [
        ("Select the chassis body", "Cube"),
        ("Create the 2D lidar", "Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D"),
        ("Place it above the wheel tops", "Translate (0.45, 0, 1.0) — Cube-local units"),
        ("Add obstacles", "Create > Mesh > Cube · Cone · Cylinder"),
    ], "say": [
        "So here is the six point one recipe.",
        "Select the cube, the chassis body.",
        "Create an RTX lidar using the NVIDIA example rotary 2 D configuration. It appears under the cube.",
        "Set its translate to zero point four five, zero, one. These are cube local units, so that means zero point nine meters forward and above the wheel tops. Any lower and the scan hits the robot's own wheels.",
        "Then scatter a few obstacles around. The RTX lidar sees any rendered surface, even without colliders.",
    ]},
    {"type": "callout", "kind": "tip", "title": "Seeing the beams", "body":
        "RTX lidars have no Draw Lines option. View the scan in RViz (lesson 1.4) or attach the point-cloud writer.",
     "code": 'LidarSensor(Lidar(path), annotators=[]).attach_writer("draw-point-cloud")',
     "say": "One more difference. The RTX lidar has no draw lines checkbox. To see its beams, either stream the scan "
            "to RViz, which is the next lesson, or attach the draw point cloud writer from the script editor, as shown "
            "in the lesson file."},
])

# ============================================================================ 1.4
lesson("1.4_ros2_and_rviz", "Lesson 1.4 — Lidar to ROS 2 and RViz", [
    {"type": "title", "eyebrow": "Module 1 · Lesson 1.4", "title": "Lidar to ROS 2 and RViz",
     "sub": "Publish a LaserScan on /scan_lidar and draw it",
     "say": "In this lesson the lidar data leaves Isaac Sim. You publish it as a ROS 2 laser scan and draw it in RViz."},
    {"type": "callout", "kind": "tip", "title": "ROS 2 in 6.1", "body":
        "Isaac Sim bundles ROS 2 Jazzy — no sourcing before launch. Install system Jazzy only for rviz2 and the ros2 CLI.",
     "code": "sudo apt install ros-jazzy-desktop",
     "say": "Good news first. Isaac Sim six point one ships its own ROS 2 Jazzy libraries, so you no longer source ROS "
            "before launching it. The reference setup is Ubuntu twenty four point zero four, which pairs with ROS 2 "
            "Jazzy; on Ubuntu twenty two point zero four use Humble. Install system ROS only for the command line tools and RViz. The setup file in the course "
            "folder has the exact commands."},
    {"type": "diagram", "title": "The data path", "img": "m1-ros2-lidar",
     "caption": "One menu builds the whole Isaac Sim side",
     "say": "This is the data path. Each frame the RTX lidar is rendered into a render product. The ROS 2 RTX lidar "
            "helper node turns it into a laser scan message on the scan lidar topic, with the frame id sim lidar. "
            "RViz subscribes to that topic and draws the points."},
    {"type": "steps", "title": "Build the graph", "bullets": [
        ("Stop the simulation, open the tool", "Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar"),
        ("Frame ID · LaserScan topic", "sim_lidar · scan_lidar"),
        ("Lidar prim · Laser Scan ✓", "/World/SimpleRobot/Cube/Example_Rotary_2D"),
        ("Play", "▶"),
    ], "say": [
        "Building it takes one dialog.",
        "Stop the simulation and open Tools, Robotics, ROS 2 OmniGraphs, RTX lidar.",
        "Set the frame id to sim lidar and the laser scan topic to scan lidar.",
        "Pick your lidar prim and tick laser scan.",
        "Click OK and press play. The topic now exists.",
    ]},
    {"type": "steps", "title": "View it in RViz", "bullets": [
        ("New terminal", "source /opt/ros/jazzy/setup.bash"),
        ("Check the topic", "ros2 topic hz /scan_lidar"),
        ("Start RViz", "rviz2"),
        ("Fixed Frame = sim_lidar, Add > By topic > LaserScan", "not the topic name!"),
    ], "say": [
        "Now look at it from ROS.",
        "Open a terminal and source ROS 2 Jazzy.",
        "Run ros2 topic hz on scan lidar. You should see about ten messages per second.",
        "Start RViz.",
        "Set the fixed frame to sim lidar. Note: the course text says to use the topic name here, but it must be the frame id. Then add a laser scan display by topic, and the obstacles appear as points.",
    ]},
    {"type": "callout", "kind": "trap", "title": "If no messages arrive", "body":
        "Simulation not playing · different ROS_DOMAIN_ID · RTX lidar on a fixed-jointed body · custom subscriber "
        "without sensor-data QoS", "code": "./python.sh learning_resource/scripts/m1_ros2_lidar.py --headless --test",
     "say": "If nothing arrives, check four things. Is the simulation playing? Do both terminals use the same ROS "
            "domain id? Is the lidar under the chassis body rather than the fixed jointed mount? And if you wrote your "
            "own subscriber, use the sensor data quality of service profile. The checkpoint script tests all of this "
            "and expects the forward beam to read two and a half meters."},
])

# ============================================================================ 2.1
lesson("2.1_importing_urdf", "Lesson 2.1 — Importing URDF assets", [
    {"type": "title", "eyebrow": "Module 2 · Lesson 2.1", "title": "Importing URDF assets",
     "sub": "Carter: from carter.urdf to a drivable USD robot",
     "say": "Most real robots come as URDF files. In this module you import Carter, a two wheeled robot with a caster, "
            "using the rewritten URDF importer in Isaac Sim six point one."},
    {"type": "diagram", "title": "The import pipeline", "img": "m2-urdf-pipeline",
     "caption": "Two new steps in 6.1: pick the physics variant, set the drives",
     "say": "Here is the pipeline. The importer converts the URDF into a USD file plus a payloads folder. New in six "
            "point one, the physics lives in a variant set with one option per engine. Until you select the physx "
            "variant, the robot has no physics at all. And the importer no longer configures drives, so you set the "
            "wheel drives yourself."},
    {"type": "steps", "title": "Import", "bullets": [
        ("Carter ships with Isaac Sim — copy included", "learning_resource/assets/carter/urdf/carter.urdf"),
        ("Open the importer", "File > Import"),
        ("Options > Base Type", "Mobile"),
        ("Import — the robot opens as its own stage", "carter/carter.usda"),
    ], "say": [
        "Let's import.",
        "You do not need the course download. The same Carter URDF ships with Isaac Sim, and a copy is in the assets folder.",
        "Use File, Import, and select carter dot u r d f.",
        "In the options panel, set the base type to mobile, because Carter drives around.",
        "Click import. The converted robot opens as a new stage.",
    ]},
    {"type": "diagram", "title": "What the importer writes", "img": "m2-carter-structure",
     "caption": "Links under Geometry · joints under Physics",
     "say": "Expand it in the stage panel. Links live under Geometry, with chassis link as the articulation root. "
            "Joints live under Physics: the two driven wheels and the two passive caster joints. And on the top prim "
            "there is the physics variant set."},
    {"type": "steps", "title": "Make it physical and drivable", "bullets": [
        ("Select carter > Variants", "Physics = physx"),
        ("left_wheel, right_wheel", "stiffness 0 · damping 10000"),
        ("rear_pivot, rear_axle", "stiffness 0 · damping 0"),
        ("Save", "File > Save"),
    ], "say": [
        "Two steps make it usable.",
        "Select carter, open variants in the property panel, and choose physx.",
        "Give the two wheel joints a velocity drive: stiffness zero and damping ten thousand.",
        "Leave the caster joints passive, with zero stiffness and zero damping.",
        "Save. Your Carter is now a drivable robot.",
    ]},
])

# ============================================================================ 2.2
lesson("2.2_preparing_the_simulation", "Lesson 2.2 — Preparing the simulation", [
    {"type": "title", "eyebrow": "Module 2 · Lesson 2.2", "title": "Preparing the simulation",
     "sub": "A scene, a joint review and keyboard driving",
     "say": "Now put Carter into a scene, check its joints, and drive it with the keyboard."},
    {"type": "steps", "title": "Build the scene", "bullets": [
        ("New stage + grid", "File > New · Create > Environments > Flat Grid"),
        ("Add the robot", "drag carter.usda in, or Import with Add Reference to Stage ✓"),
        ("Pick the variant again on this reference", "Variants > Physics = physx"),
        ("Lift and test", "Translate Z = 0.05 · Play"),
    ], "say": [
        "First the scene.",
        "Start a new stage and add a flat grid from Create, Environments.",
        "Bring in Carter, either by dragging carter dot u s d a from the content browser, or by importing again with add reference to stage ticked.",
        "The variant choice is stored per reference, so select physx again on this one.",
        "Lift it five centimeters and press play. Carter drops onto the grid.",
    ]},
    {"type": "steps", "title": "Quick drive test", "bullets": [
        ("Both wheel joints", "Target Velocity = 20 °/s"),
        ("Play — slow straight line", "≈ 0.08 m/s"),
        ("One wheel to 0 while playing", "it turns"),
        ("No 4.2 articulation-root fix needed", "importer puts it on chassis_link"),
    ], "say": [
        "Before adding a controller, test the joints directly.",
        "Set both wheel targets to twenty degrees per second.",
        "Press play. Carter rolls slowly forward, about eight centimeters per second.",
        "Set one wheel back to zero while it plays, and Carter turns.",
        "The course had an articulation root fix for version four point two. You can skip it: the importer already puts the root on chassis link.",
    ]},
    {"type": "diagram", "title": "Where the controller numbers come from", "img": "m2-carter-drive",
     "caption": "Read them from the URDF, not from guesses",
     "say": "Now the differential controller with keyboard control, same menu as before. Its two numbers come from the "
            "URDF. The wheel radius is the wheel cylinder radius, zero point two four. The distance between wheels is "
            "twice the joint offset of zero point three one four, so about zero point six three."},
    {"type": "callout", "kind": "tip", "title": "Limit the speed", "body":
        "The keyboard graph commands large speeds. On the Differential Controller node set maxLinearSpeed 0.5 and "
        "maxAngularSpeed 1.0.", "code": "./python.sh learning_resource/scripts/m2_import_carter.py --headless --test",
     "say": "Finally, the keyboard graph asks for big speeds and Carter gets erratic. On the controller node set max "
            "linear speed to zero point five and max angular speed to one. The m2 checkpoint script does this whole "
            "lesson automatically and checks that Carter drives forward."},
])

# ============================================================================ 2.3
lesson("2.3_adding_sensors", "Lesson 2.3 — Adding sensors to Carter", [
    {"type": "title", "eyebrow": "Module 2 · Lesson 2.3", "title": "Adding sensors to Carter",
     "sub": "Camera and RTX lidar on chassis_link",
     "say": "Carter imported from URDF has no sensors. In this lesson you add a camera and a lidar, applying what you "
            "learned in module one."},
    {"type": "diagram", "title": "The sensor layout", "img": "m2-carter-sensors",
     "caption": "Both sensors sit directly under the chassis body",
     "say": "Both sensors go directly under chassis link, the chassis body. That follows the six point one rule from "
            "lesson one point three. The camera feeds a viewport. The lidar sees every rendered obstacle, and you can "
            "stream it to RViz with the graph from lesson one point four."},
    {"type": "steps", "title": "Camera", "bullets": [
        ("Create > Camera, drag under", "carter / Geometry / chassis_link"),
        ("Rename · transform", "RGB_Sensor · T (0.1, 0, 0.33) · R (90, -90, 0)"),
        ("Check the view", "Cameras > RGB_Sensor"),
        ("Play and drive", "W A S D"),
    ], "say": [
        "Start with the camera.",
        "Create a camera and drag it under carter, Geometry, chassis link.",
        "Rename it R G B sensor, translate it to zero point one, zero, zero point three three, and rotate it ninety, minus ninety, zero.",
        "Look through it from the viewport camera menu.",
        "Press play and drive. The view moves with Carter.",
    ]},
    {"type": "steps", "title": "Lidar and obstacles", "bullets": [
        ("Select chassis_link", "Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D"),
        ("Translate", "(-0.05, 0, 0.42)"),
        ("Obstacles", "Create > Mesh > Cube / Sphere / Cylinder"),
        ("Colliders for contact, not for detection", "Add > Physics > Rigid Body with Colliders Preset"),
    ], "say": [
        "Then the lidar.",
        "Select chassis link and create the example rotary 2 D RTX lidar.",
        "Translate it to minus zero point zero five, zero, zero point four two.",
        "Add a few obstacles around the grid.",
        "Give them colliders so Carter bumps into them. Unlike the course's PhysX lidar, the RTX lidar does not need colliders to see them. Remember to switch the viewport back to perspective before navigating.",
    ]},
])

# ============================================================================ 2.4
lesson("2.4_nova_carter", "Lesson 2.4 — Nova Carter", [
    {"type": "title", "eyebrow": "Module 2 · Lesson 2.4", "title": "Accessing a prepared robot",
     "sub": "NVIDIA's Nova Carter with its full sensor suite",
     "say": "You have now built a robot by hand twice. In this short lesson you load one that NVIDIA prepared: Nova "
            "Carter, with physics, drives and a complete sensor suite."},
    {"type": "steps", "title": "Load it", "bullets": [
        ("New stage + grid", "File > New · Create > Environments > Flat Grid"),
        ("Add the robot", "Create > Robots > Nova Carter with Sensors"),
        ("Optional: finished URDF Carter", "Window > Browsers > Isaac Sim Assets · search carter"),
        ("First load can take minutes", "assets stream from NVIDIA's server"),
    ], "say": [
        "Loading it is easy.",
        "Start a new stage with a flat grid.",
        "Choose Create, Robots, Nova Carter with sensors.",
        "If you like, also open Window, Browsers, Isaac Sim Assets and search for carter to find the finished version of the robot you imported.",
        "The first load can take a few minutes, because the assets stream from NVIDIA's server.",
    ]},
    {"type": "diagram", "title": "What's inside", "img": "m2-nova-carter",
     "caption": "Every sensor sits under the chassis body",
     "say": "Expand chassis link. Under sensors you find two 2 D lidars, an RPLidar at the front and back, a Hesai X T "
            "thirty two 3 D lidar on top, four Hawk stereo cameras with I M Us, and four Owl fisheye cameras. Two driven "
            "wheel joints and two passive casters complete it. Notice that every sensor sits under the chassis body, "
            "exactly the rule you learned."},
    {"type": "callout", "kind": "tip", "title": "Harmless warnings", "body":
        "“Projection type 'fisheyePolynomial' is deprecated” for Owl/Hawk cameras is expected in 6.1.",
     "code": None,
     "say": "In the console you may see warnings that the fisheye polynomial projection is deprecated. They are "
            "harmless. In module four you will drive this robot from ROS 2."},
])

# ============================================================================ 3.1
lesson("3.1_synthetic_data", "Module 3 — Synthetic data with Replicator", [
    {"type": "title", "eyebrow": "Module 3", "title": "Synthetic data generation",
     "sub": "A pallet-jack detection dataset with Replicator",
     "say": "Perception models need thousands of labeled images. In this module Isaac Sim produces them for you: a "
            "warehouse full of randomized pallet jacks, written out as a labeled KITTI dataset."},
    {"type": "steps", "title": "Domain randomization in one slide", "bullets": [
        ("Vary what doesn't matter", "camera · pose · color · lights · textures"),
        ("Keep what matters: the object", "pallet jack"),
        ("Model learns the object, not the scene", "closes the sim-to-real gap"),
        ("Labels come for free", "boxes from the renderer"),
    ], "say": [
        "The idea is called domain randomization.",
        "You vary everything that should not matter: where the camera is, how objects are placed and colored, the lights and the floor textures.",
        "The object you care about, the pallet jack, stays.",
        "So the model learns the object itself rather than one particular scene, which narrows the gap between simulation and reality.",
        "And because the renderer knows where everything is, every bounding box label comes for free.",
    ]},
    {"type": "diagram", "title": "The 6.1 pipeline", "img": "m3-sdg-pipeline",
     "caption": "Randomize in Python, then step the orchestrator",
     "say": "Here is the pipeline. Load the warehouse, add six pallet jacks and twelve distractor props, keep labels "
            "only on the pallet jacks, and attach a camera with a KITTI writer. Then, for every frame, randomize, step "
            "the orchestrator, and the writer saves the image and its labels."},
    {"type": "callout", "kind": "trap", "title": "Why the script differs from the course", "body":
        "Graph randomizers fired only on the first step() · material randomizer hung · warehouse labels came from "
        "referenced layers", "code": "functional API: rep.functional.modify.pose / attribute / visibility",
     "say": "The course script does not work unchanged in six point one. On this build, the graph randomizers fired "
            "only on the first frame, so every image was identical, and the material randomizer hung for more than ten "
            "minutes. The port uses the functional API instead, which is also what the six point one examples use, and "
            "it blocks the warehouse labels that come from referenced files."},
    {"type": "steps", "title": "Run it", "bullets": [
        ("Quick look, 20 frames", "./python.sh learning_resource/scripts/m3_palletjack_sdg.py"),
        ("Full dataset, headless", "--headless --num_frames 2000"),
        ("Output", "output/palletjack_data/warehouse/Camera/"),
        ("Train outside Isaac Sim", "course repo notebooks (TAO / PyTorch)"),
    ], "say": [
        "Running it is one command.",
        "For a quick look, run the m3 pallet jack script with a window. It makes twenty frames.",
        "For the real dataset, run it headless with two thousand frames.",
        "The images and KITTI labels land in the output folder, under Camera.",
        "Training the detector happens outside Isaac Sim, with the course repository's notebooks, and nothing there changes for six point one.",
    ]},
])

# ============================================================================ 4.1
lesson("4.1_omnigraph_cmd_vel", "Lesson 4.1 — Driving from ROS 2", [
    {"type": "title", "eyebrow": "Module 4 · Lesson 4.1", "title": "Driving Nova Carter from ROS 2",
     "sub": "Software-in-the-loop: /cmd_vel into an Action Graph",
     "say": "Software in the loop means your real robot software talks to the simulated robot instead of real "
            "hardware. The simplest case: a ROS 2 velocity command drives Nova Carter."},
    {"type": "diagram", "title": "The control loop", "img": "m4-cmd-vel",
     "caption": "The graph the lesson builds by hand",
     "say": "Here is the loop. Teleop twist keyboard publishes a twist message on the cmd vel topic. In Isaac Sim, the "
            "subscribe twist node receives it, two break vector nodes take the forward speed and the turning speed, "
            "the differential controller computes wheel speeds, and the articulation controller drives the two wheel "
            "joints."},
    {"type": "steps", "title": "Build the graph", "bullets": [
        ("Scene", "Create > Environments > Simple Room · Create > Robots > Nova Carter"),
        ("New graph on the robot", "Create > Visual Scripting > Action Graph"),
        ("Diff. Controller", "wheelRadius 0.14 · wheelDistance 0.413 · max 2.0 / 3.0"),
        ("Articulation Controller target · joints", "chassis_link · joint_wheel_left/right"),
    ], "say": [
        "Build it like this.",
        "Create the simple room and add Nova Carter.",
        "Right click the robot and create an action graph. Add the nodes in the table of the lesson file. The wiring is written out there in text, because the course only shows a picture.",
        "Set the differential controller to wheel radius zero point one four and wheel distance zero point four one three.",
        "Point the articulation controller at chassis link and give it the two wheel joint names.",
    ]},
    {"type": "steps", "title": "Drive from a terminal", "bullets": [
        ("Play, then in a sourced terminal", "ros2 topic list"),
        ("One command", 'ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}"'),
        ("Keyboard teleop", "ros2 run teleop_twist_keyboard teleop_twist_keyboard"),
        ("i forward · , back · j / l turn · k stop", None),
    ], "say": [
        "Now drive it from ROS.",
        "Press play and list topics in a terminal with ROS 2 Jazzy sourced. You should see cmd vel.",
        "Publish one twist message with a forward speed of zero point two, and Carter moves.",
        "Then start teleop twist keyboard.",
        "Use i to go forward, comma to go back, j and l to turn, and k to stop. The checkpoint script for this lesson publishes real ROS messages and checks that the robot follows them.",
    ]},
])

# ============================================================================ 4.2
lesson("4.2_python_scripting", "Lesson 4.2 — Python scripting", [
    {"type": "title", "eyebrow": "Module 4 · Lesson 4.2", "title": "Foundations of Python scripting",
     "sub": "Script Editor, USD API, the 6.1 core API and standalone apps",
     "say": "Everything you clicked so far can be scripted. This lesson shows three ways to create the same scene in "
            "Python: the raw USD API, the Isaac Sim core API, and a standalone application."},
    {"type": "diagram", "title": "The layers you script against", "img": "m4-python-layers",
     "caption": "omni.isaac.core is gone — use isaacsim.core.experimental",
     "say": "Here are the layers. At the bottom are the engines. Above them, OpenUSD, the pxr modules, which are stable "
            "across versions. Then Kit and the omni services, and on top the Isaac Sim core experimental API. The "
            "course used omni dot isaac dot core, which was removed, and its successor in version five is now "
            "deprecated too."},
    {"type": "steps", "title": "Script Editor", "bullets": [
        ("Open it", "Window > Script Editor"),
        ("Run everything · run a selection", "Ctrl+Enter · Run Selected"),
        ("USD snippet works unchanged", "scripts/m4_snippet_usd_api.py"),
        ("Core API snippet rewritten for 6.1", "scripts/m4_snippet_core_api.py"),
    ], "say": [
        "Start with the script editor.",
        "Open it from the Window menu.",
        "Control enter runs the whole tab, and run selected runs only the highlighted lines.",
        "The course's USD API snippet still works exactly as written. Paste it on an empty stage and press play.",
        "The core API snippet had to be rewritten. Its six point one version is in the scripts folder.",
    ]},
    {"type": "steps", "title": "What changed in the core API", "bullets": [
        ("DynamicCuboid → shape + physics wrappers", "Cube + RigidPrim + GeomPrim(apply_collision_apis=True)"),
        ("Batched arguments", "position → positions · scale → scales"),
        ("Colors via materials", "PreviewSurfaceMaterial"),
        ("Standalone app", "from isaacsim import SimulationApp"),
    ], "say": [
        "Four changes to remember.",
        "Dynamic cuboid is split into a cube shape, a rigid prim for the body and a geom prim for the collider.",
        "Arguments are plural, because every wrapper can handle many prims at once.",
        "Colors come from a preview surface material.",
        "And standalone scripts import SimulationApp from isaacsim. That must be the first import. Every checkpoint script in this course is such an app, so they are good examples to read.",
    ]},
])

# ============================================================================ 4.3
lesson("4.3_isaac_ros_segmentation", "Lesson 4.3 — Isaac ROS segmentation", [
    {"type": "title", "eyebrow": "Module 4 · Lesson 4.3", "title": "Image segmentation in the loop",
     "sub": "Isaac Sim cameras feeding Isaac ROS",
     "say": "The last software in the loop lessons connect Isaac Sim's cameras to Isaac ROS, NVIDIA's GPU accelerated "
            "ROS packages, here for image segmentation."},
    {"type": "diagram", "title": "The setup", "img": "m4-sil-segmentation",
     "caption": "Most of the work happens on the Isaac ROS side",
     "say": "The Hawk camera on Nova Carter publishes images on the r g b topic through a ROS 2 camera graph. An Isaac "
            "ROS segmentation container processes them, and you can view the result or let your own node react and "
            "send velocity commands back."},
    {"type": "steps", "title": "Isaac Sim side", "bullets": [
        ("Scene from lesson 4.1", "Nova Carter in the Simple Room"),
        ("Camera graph", "Tools > Robotics > ROS 2 OmniGraphs > Camera"),
        ("Camera prim · RGB ✓", "chassis_link/sensors/front_hawk/left/camera_left"),
        ("Check", "ros2 topic hz /rgb · rqt_image_view"),
    ], "say": [
        "Only the Isaac Sim side changes in six point one.",
        "Start from the Nova Carter scene of lesson four point one.",
        "Open Tools, Robotics, ROS 2 OmniGraphs, Camera.",
        "Pick the front Hawk left camera and tick R G B.",
        "Press play and check the rate of the r g b topic, or view it with r q t image view.",
    ]},
    {"type": "callout", "kind": "trap", "title": "Distro mismatch", "body":
        "Isaac ROS containers are often Humble; Isaac Sim publishes with Jazzy. Keep the same RMW and domain ID — or "
        "launch Isaac Sim with the container's distro.", "code": "export ROS_DISTRO=humble && ./isaac-sim.sh",
     "say": "One thing to watch: Isaac ROS containers often use ROS 2 Humble, while Isaac Sim publishes with Jazzy. "
            "Standard messages usually still flow if both sides use the same middleware and domain id. If they do not, "
            "start Isaac Sim with ROS distro set to humble. Six point one bundles both."},
])

# ============================================================================ 5
lesson("5_hardware_in_the_loop", "Module 5 — Hardware-in-the-loop", [
    {"type": "title", "eyebrow": "Module 5", "title": "Hardware-in-the-loop",
     "sub": "The same simulation, a real Jetson",
     "say": "In hardware in the loop, the robot's real computer, an NVIDIA Jetson, runs the robot software, while Isaac "
            "Sim on your workstation simulates the world and the sensors."},
    {"type": "diagram", "title": "The deployment", "img": "m5-hil",
     "caption": "Sensors out, /cmd_vel back, over the LAN",
     "say": "Isaac Sim publishes clock, scan and camera topics. They travel over the local network as DDS traffic to "
            "the Jetson, where Isaac ROS and your perception or navigation nodes run. Velocity commands come back the "
            "same way."},
    {"type": "steps", "title": "Checklist on the Isaac Sim side", "bullets": [
        ("Same network, same domain, same RMW", "ROS_DOMAIN_ID · rmw_fastrtps_cpp"),
        ("Publish simulated time", "Tools > Robotics > ROS 2 OmniGraphs > Clock"),
        ("Jetson nodes use sim time", "use_sim_time: true"),
        ("Distro mismatch?", "export ROS_DISTRO=humble before ./isaac-sim.sh"),
    ], "say": [
        "Four things to check on the simulation side.",
        "Both machines on the same network, with the same domain id and middleware.",
        "Publish the simulation clock with the clock graph.",
        "Set use sim time to true for the nodes on the Jetson.",
        "And if the Jetson runs Humble, launch Isaac Sim with the Humble libraries. The Jetson setup itself follows the course pages unchanged. That completes the course. Congratulations, and enjoy building robots in Isaac Sim six point one.",
    ]},
])
