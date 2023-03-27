<img src="assets/easyrobot.png" alt="easyrobot" height=200 />

# easyrobot

An easy and unified interface for robots (and grippers, *etc.*)

## Setup

Follow the [robot installation manual](docs/install/robot.md) to install the robot dependencies.

Then execute the following commands:

```bash
git clone git@github.com:Galaxies99/easyrobot.git
cd easyrobot
python setup.py install
```

Finally, `import easyrobot`!

## Supported Devices

- **Robot**(`.robot`). Flexiv Robot.

- **Gripper**(`.gripper`). Robotiq 2F-85, Robotiq 2F-140, Dahuan AG95.

- **Pedal**(`.pedal`). Logitech G29.

- **Force/Torque Sensor**(`.ftsensor`). ATI, OptoForce.
