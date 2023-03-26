'''
Robot Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.gripper.api import get_gripper
from easyrobot.utils.shm import SharedMemoryManager


class RobotBase(object):
    def __init__(
        self, 
        gripper: dict = {},
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ): 
        '''
        Initialization.
        
        Parameters:
        - gripper: dict, optional, default: {}, the gripper parameters;
        - shm_name: str, optional, default: "none", the shared memory name of the robot data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(RobotBase, self).__init__()
        self.is_streaming = False
        self.gripper = get_gripper(**gripper)
        self.with_streaming = (shm_name != "none")
        self.streaming_freq = streaming_freq
        self.shm_name = shm_name
        self._prepare_shm()

    def _prepare_shm(self):
        '''
        Prepare shared memory objects.
        '''
        if self.with_streaming:
            info = np.array(self.get_info()).astype(np.float64)
            self.shm_robot = SharedMemoryManager(self.shm_name, 0, info.shape, info.dtype)
            self.shm_robot.execute(info)
        
    def streaming(self, delay_time = 0.0):
        '''
        Start streaming.
        
        Parameters:
        - delay_time: float, optional, default: 5.0, the delay time before collecting data.
        '''
        if self.with_streaming is False:
            raise AttributeError('If you want to use streaming function, the "shm_name" attribute should be set correctly.')
        self.thread = threading.Thread(target = self.streaming_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
    
    def streaming_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_streaming = True
        logging.info('[Robot] Start streaming ...')
        while self.is_streaming:
            self.shm_robot.execute((self.get_info()).astype(np.float64))
            time.sleep(1.0 / self.streaming_freq)
    
    def stop_streaming(self, permanent = True):
        '''
        Stop streaming process.

        Parameters:
        - permanent: bool, optional, default: True, whether the streaming process is stopped permanently.
        '''
        self.is_streaming = False
        self.thread.join()
        logging.info('[Robot] Close streaming.')
        if permanent:
            self._close_shm()
            self.with_streaming = False
    
    def _close_shm(self):
        '''
        Close shared memory objects.
        '''
        if self.with_streaming:
            self.shm_robot.close()

    def get_info(self):
        '''
        Get the robot information.
        '''
        return np.array([])

    def send_tcp_pose(self, pose, wait = False, **kwargs):
        '''
        Send the TCP pose to the robot.
        '''
        pass

    def send_joint_pos(self, pos, wait = False, **kwargs):
        '''
        Send the joint position to the robot.
        '''
        pass
    
    def get_tcp_pose(self):
        '''
        Get the TCP pose from the robot.
        '''
        pass

    def get_joint_pose(self):
        '''
        Get the joint pose from the robot.
        '''
        pass
    
    def open_gripper(self):
        '''
        Open the gripper.
        '''
        self.gripper.open_gripper()

    def close_gripper(self):
        '''
        Close the gripper.
        '''
        self.gripper.close_gripper()
    
    def gripper_action(self, position, **kwargs):
        '''
        Perform unified gripper action.
        '''
        self.gripper.action(position, **kwargs)

    def get_gripper_info(self):
        '''
        Get the gripper information.
        '''
        return self.gripper.get_info()

    def action(self, action_dict, wait = False, **kwargs):
        '''
        Unified robot action.
        '''
        pass
