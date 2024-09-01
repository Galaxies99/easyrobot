'''
Flexiv robot interface, built upon Flexiv RDK: https://github.com/flexivrobotics/flexiv_rdk/

Author: Hongjie Fang, Junfeng Ding.
'''
import time
import numpy as np

from easyrobot.robot import flexivrdk
from easyrobot.robot.base import RobotBase


class FlexivRobotModeMap:
    idle = "MODE_IDLE"
    plan = "MODE_PLAN_EXECUTION"
    primitive = "MODE_PRIMITIVE_EXECUTION"
    cart_impedance_online = "MODE_CARTESIAN_IMPEDANCE_NRT"
    cart_impedance_stream = "MODE_CARTESIAN_IMPEDANCE"
    joint_position_online = "MODE_JOINT_POSITION_NRT"
    joint_position_stream = "MODE_JOINT_POSITION"
    joint_torque_stream = "MODE_JOINT_TORQUE"


class FlexivRobot(RobotBase):
    '''
    Flexiv Robot Interface.
    '''
    def __init__(
        self, 
        robot_ip_address, 
        pc_ip_address,
        gripper = {},
        logger_name: str = "Flexiv Robot",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - robot_ip_address: str, required, the ip address of the robot;
        - pc_ip_address: str, required, the ip address of the pc;
        - gripper: dict, optional, default: {}, the gripper parameters;
        - logger_name: str, optional, default: "Fleixv Robot", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the robot data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        self.robot = flexivrdk.Robot(robot_ip_address, pc_ip_address)
        self.mode = flexivrdk.Mode
        self.robot_states = flexivrdk.RobotStates()
        self.enable()
        self.DOF = len(self.get_robot_states().q)
        super(FlexivRobot, self).__init__(
            gripper = gripper,
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq, 
            **kwargs
        )
        self.logger.info("Robot is now operational.")
    
    def enable(self):
        '''
        Enable the robot.
        '''
        # Clear fault on robot server if any
        if self.is_fault():
            self.clear_fault()
            time.sleep(2)
            if self.is_fault():
                raise RuntimeError("The fault of the robot cannot be cleared.")
        
        # Enable the robot, make sure the E-stop is released before enabling
        self.robot.enable()

        # Wait for the robot to become operational
        seconds_waited = 0
        while not self.is_operational():
            time.sleep(1)
            seconds_waited += 1
        

    def clear_fault(self):
        self.robot.clearFault()

    def is_fault(self):
        '''
        Check if robot is in FAULT state.
        '''
        return self.robot.isFault()

    def is_stopped(self):
        '''
        Check if robot is stopped.
        '''
        return self.robot.isStopped()

    def is_connected(self):
        '''
        Return if connected.
        '''
        return self.robot.isConnected()

    def is_operational(self):
        '''
        Check if robot is operational.
        '''
        return self.robot.isOperational()

    def mode_mapper(self, mode):
        assert mode in FlexivRobotModeMap.__dict__.keys(), "unknown mode name: %s" % mode
        return getattr(self.mode, getattr(FlexivRobotModeMap, mode))

    def get_mode(self):
        return self.robot.getMode()

    def set_mode(self, mode):
        control_mode = self.mode_mapper(mode)
        self.robot.setMode(control_mode)
    
    def switch_mode(self, mode, sleep_time=0.01):
        '''
        Switch to different control modes.

        Parameters:
        - mode: 'joint_position_online', 'joint_position_stream', 'cart_impedance_online', 'cart_impedance_stream', 'plan', 'primitive';
        - sleep_time: sleep time to control mode switch time.
        '''
        if self.get_mode() == self.mode_mapper(mode):
            return

        while self.get_mode() != self.mode_mapper("idle"):
            self.set_mode("idle")
            time.sleep(sleep_time)
        while self.get_mode() != self.mode_mapper(mode):
            self.set_mode(mode)
            time.sleep(sleep_time)

        self.logger.info("Set mode: {}".format(str(self.get_mode())))
    
    def execute_primitive(self, cmd):
        '''
        Execute primitive.

        Parameters:
        - cmd: primitive command string, e.x. "ptName(inputParam1=xxx, inputParam2=xxx, ...)"
        '''
        self.switch_mode("primitive")
        self.logger.info("Execute primitive: {}".format(cmd))
        self.robot.executePrimitive(cmd)
    
    def send_tcp_pose(
        self, 
        pose, 
        wait = False,
        max_wrench = np.array([100.0, 100.0, 100.0, 30.0, 30.0, 30.0]),
        **kwargs
    ):
        '''
        Send TCP pose (non real-time).

        Parameters:
        - pose: 7-dim list or numpy array, target pose (x, y, z, rw, rx, ry, rz) in world frame;
        - wrench: 6-dim list or numpy array, max moving force (fx, fy, fz, wx, wy, wz).
        '''
        self.switch_mode("cart_impedance_online")
        self.robot.sendTcpPose(np.array(pose), np.array(max_wrench))
        if wait:
            self.wait_until_tcp(np.array(pose), **kwargs)
    
    def stream_tcp_pose(
        self, 
        pose, 
        max_wrench = np.array([100.0, 100.0, 100.0, 30.0, 30.0, 30.0])
    ):
        '''
        Stream TCP pose (real-time).

        Parameters:
        - pose: 7-dim list or numpy array, target pose (x, y, z, rw, rx, ry, rz) in world frame;
        - wrench: 6-dim list or numpy array, max moving force (fx, fy, fz, wx, wy, wz).
        '''
        self.switch_mode("cart_impedance_stream")
        self.robot.streamTcpPose(np.array(pose), np.array(max_wrench))
    
    def send_joint_pos(
        self, 
        pos, 
        wait = False,
        vel = np.array([0, 0, 0, 0, 0, 0, 0]), 
        acc = np.array([0, 0, 0, 0, 0, 0, 0]), 
        max_vel = np.array([2, 2, 2, 2, 2, 2, 2]), 
        max_acc = np.array([3, 3, 3, 3, 3, 3, 3]),
        **kwargs
    ):
        '''
        Send joint pose (non real-time).

        Parameters:
        - pos: DOF-dim list or numpy array, target joint position of DOF joints;
        - vel: DOF-dim list or numpy array, target joint velocity of DOF joints;
        - acc: DOF-dim list or numpy array, target joint acceleration of DOF joints;
        - max_vel: DOF-dim list or numpy array, maximum joint velocity of DOF joints;
        - max_acc: DOF-dim list or numpy array, maximum joint acceleration of DOF joints.
        '''
        self.switch_mode("joint_position_online")
        self.robot.sendJointPosition(np.array(pos), np.array(vel), np.array(acc), np.array(max_vel), np.array(max_acc))
        if wait:
            self.wait_until_joint(np.array(pos), **kwargs)
    
    def stream_joint_pos(
        self,
        pos, 
        vel = np.array([0, 0, 0, 0, 0, 0, 0]), 
        acc = np.array([0, 0, 0, 0, 0, 0, 0])
    ):
        '''
        Send joint pose (real-time).

        Parameters:
        - pos: DOF-dim list or numpy array, target joint position of DOF joints;
        - vel: DOF-dim list or numpy array, target joint velocity of DOF joints;
        - acc: DOF-dim list or numpy array, target joint acceleration of DOF joints.
        '''
        self.switch_mode("joint_position_stream")
        self.robot.streamJointPosition(pos, vel, acc)
    
    def execute_plan_by_name(
        self,
        name,
    ):
        '''
        Execute plan by name.
        
        Parameters:
        - name: string of plan name.
        '''
        self.switch_mode("plan")
        self.robot.executePlanByName(name)

    def execute_plan_by_index(self, index):
        '''
        Execute plan by index.
        
        Parameters:
        - index: int, index of plan.
        '''
        self.switch_mode("plan")
        self.robot.executePlanByIndex(index)

    def get_robot_states(self):
        self.robot.getRobotStates(self.robot_states)
        return self.robot_states

    def get_joint_pos(self):
        '''
        Get the joint position.
        '''
        return np.array(self.get_robot_states().q.copy())
    
    def get_joint_vel(self):
        '''
        Get the joint velocity.
        '''
        return np.array(self.get_robot_states().dq.copy())

    def get_tcp_pose(self):
        '''
        Get the tcp pose.
        '''
        return np.array(self.get_robot_states().tcpPose.copy())
    
    def get_tcp_vel(self):
        '''
        Get the tcp velocity.
        '''
        return np.array(self.get_robot_states().tcpVel.copy())
    
    def get_force_torque_tcp(self):
        '''
        Get the force torque information in the tcp frame.
        '''
        return np.array(self.get_robot_states().extWrenchInTcp.copy())
    
    def get_force_torque_base(self):
        '''
        Get the force torque information in the base frame.
        '''
        return np.array(self.get_robot_states().extWrenchInBase.copy())

    def wait_until_joint(self, target_joint_pos, joint_threshold = 0.05, required_freq = 100, **kwargs):
        '''
        Wait until the robot move to the target joint position.
        '''
        waiting_time = 1.0 / required_freq
        while True:
            if np.abs(np.array(target_joint_pos) - self.get_joint_pos()).max() <= joint_threshold:
                return
            time.sleep(waiting_time)

    def wait_until_tcp(self, target_tcp_pose, xyz_threshold = 0.05, quat_threshold = 0.05, required_freq = 100, **kwargs):
        '''
        Wait until the robot move to the target joint position.
        '''
        waiting_time = 1.0 / required_freq
        while True:
            tcp_pose = self.get_tcp_pose()
            if np.abs(np.array(target_tcp_pose)[:3] - tcp_pose[:3]).max() <= xyz_threshold and \
                np.abs(np.array(target_tcp_pose)[3:] - tcp_pose[3:]).max() <= quat_threshold:
                return
            time.sleep(waiting_time)

    def get_info(self):
        '''
        Get the full information, including.
        - joint position and velocity;
        - tcp pose and velocity;
        - force torque in the base/tcp frame.
        '''
        state = self.get_robot_states()
        return np.concatenate([
            state.q.copy(),               # 0:7 joint pos
            state.dq.copy(),              # 7:14 joint vel
            state.tcpPose.copy(),         # 14:21 tcp pose
            state.tcpVel.copy(),          # 21:27 tcp vel
            state.extWrenchInTcp.copy(),  # 27:33 wrench in tcp
            state.extWrenchInBase.copy()  # 33:39 wrench in base
        ]).astype(np.float32)

    def stop(self):
        super(FlexivRobot, self).stop()
        self.robot.stop()
