'''
Virtual Gripper Interface.

Author: Hongjie Fang.
'''

import numpy as np

from easyrobot.gripper.base import GripperBase


class VirtualGripper(GripperBase):
    def __init__(
        self, 
        info_shape = [],
        logger_name: str = "Virtual Gripper",
        shm_name: str = None,
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - info_shape: tuple of int, optional, default: [], the shape of the gripper information;
        - logger_name: str, optional, default: "Gripper", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the gripper data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        self.info_shape = info_shape
        self.info = np.zeros(self.info_shape, dtype = np.int64)
        super(VirtualGripper, self).__init__(
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
    
    def get_info(self):
        '''
        Get the gripper information.
        '''
        return self.info

    def set_info(self, info):
        '''
        Set the gripper information.
        '''
        assert self.info.shape == info.shape
        self.info = info
    