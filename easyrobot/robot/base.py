'''
Robot Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.gripper.api import get_gripper
from easyrobot.utils.logger import ColoredLogger
from easyrobot.utils.shared_memory import SharedMemoryManager


class RobotBase(object):
    def __init__(
        self, 
        gripper: dict = {},
        logger_name: str = "Robot",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ): 
        '''
        Initialization.
        
        Parameters:
        - gripper: dict, optional, default: {}, the gripper parameters;
        - logger_name: str, optional, default: "Robot", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the robot data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(RobotBase, self).__init__()
        logging.setLoggerClass(ColoredLogger)
        self.logger = logging.getLogger(logger_name)
        self.is_streaming = False
        self.gripper = get_gripper(**gripper)
        self.with_streaming = (shm_name is not None)
        self.streaming_freq = streaming_freq
        self.shm_name = shm_name
        self._prepare_shm()

    def _prepare_shm(self):
        '''
        Prepare shared memory objects.
        '''
        if self.with_streaming:
            info = np.array(self.get_info()).astype(np.float32)
            self.shm_robot = SharedMemoryManager(self.shm_name, 0, info.shape, info.dtype)
            self.shm_robot.execute(info)
        
    def streaming(self, delay_time = 0.0):
        '''
        Start streaming.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        if self.with_streaming is False:
            raise AttributeError('If you want to use streaming function, the "shm_name" attribute should be set correctly.')
        self.thread = threading.Thread(target = self.streaming_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
        try:
            self.gripper.streaming()
        except Exception:
            pass
    
    def streaming_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_streaming = True
        self.logger.info('Start streaming ...')
        while self.is_streaming:
            self.shm_robot.execute((self.get_info()).astype(np.float32))
            time.sleep(1.0 / self.streaming_freq)
    
    def stop_streaming(self, permanent = True):
        '''
        Stop streaming process.

        Parameters:
        - permanent: bool, optional, default: True, whether the streaming process is stopped permanently.
        '''
        self.is_streaming = False
        self.thread.join()
        self.logger.info('Close streaming.')
        if permanent:
            self._close_shm()
            self.with_streaming = False
        try:
            self.gripper.stop_streaming(permanent = permanent)
        except Exception:
            pass
    
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
    
    def stream_tcp_pose(self, pose, **kwargs):
        '''
        Stream the TCP pose to the robot.
        '''
        pass

    def send_joint_pos(self, pos, wait = False, **kwargs):
        '''
        Send the joint position to the robot.
        '''
        pass

    def stream_joint_pos(self, pos, **kwargs):
        '''
        Stream the joint position to the robot.
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

    def action(self, *args, **kwargs):
        '''
        Unified robot action.
        '''
        pass

    def stop(self):
        '''
        Stop.
        '''
        if self.is_streaming:
            self.stop_streaming(permanent = True)
        else:
            self._close_shm()