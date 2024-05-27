'''
Force/Torque Sensor Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.sensor.base import SensorBase


class FTSensorBase(SensorBase):
    def __init__(
        self, 
        logger_name: str = "F/T Sensor",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - logger_name: str, optional, default: "F/T Sensor", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the force/torque sensor data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(FTSensorBase, self).__init__(
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq
        )
    
    def get_force(self):
        '''
        Get the force sensor information.
        '''
        pass

    def get_torque(self):
        '''
        Get the torque sensor information.
        '''

    def get_info(self):
        '''
        Get the force/torque sensor information.
        '''
        return np.array([])

    def action(self, *args, **kwargs):
        '''
        Unified force/torque sensor action.
        '''
        pass
