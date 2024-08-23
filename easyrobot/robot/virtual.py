'''
Virtual Robot Interface.

Author: Hongjie Fang.
'''

import numpy as np

from easyrobot.robot.base import RobotBase


class VirtualRobot(RobotBase):
    def __init__(
        self, 
        info_shape = [],
        gripper: dict = {},
        logger_name: str = "Virtual Robot",
        shm_name: str = None,
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - info_shape: tuple of int, optional, default: [], the shape of the robot information;
        - gripper: dict, optional, default: {}, the gripper parameters;
        - logger_name: str, optional, default: "Gripper", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the gripper data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        self.info_shape = info_shape
        self.info = np.zeros(self.info_shape, dtype = np.float32)
        super(VirtualRobot, self).__init__(
            gripper = gripper,
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
    
    def get_info(self):
        '''
        Get the robot information.
        '''
        return self.info

    def set_info(self, info):
        '''
        Set the robot information.
        '''
        assert self.info.shape == info.shape
        self.info = info
    