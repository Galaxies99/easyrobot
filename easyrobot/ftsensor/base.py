'''
Force/Torque Sensor Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.utils.logger import ColoredLogger
from easyrobot.utils.shm import SharedMemoryManager


class FTSensorBase(object):
    def __init__(
        self, 
        logger_name: str = "F/T Sensor",
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - logger_name: str, optional, default: "F/T Sensor", the name of the logger;
        - shm_name: str, optional, default: "none", the shared memory name of the force/torque sensor data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(FTSensorBase, self).__init__()
        logging.setLoggerClass(ColoredLogger)
        self.logger = logging.getLogger(logger_name)
        self.is_streaming = False
        self.with_streaming = (shm_name != "none")
        self.streaming_freq = streaming_freq
        self.shm_name = shm_name
        self._prepare_shm()
    
    def _prepare_shm(self):
        '''
        Prepare shared memory objects.
        '''
        if self.with_streaming:
            info = np.array(self.get_info()).astype(np.int64)
            self.shm_ftsensor = SharedMemoryManager(self.shm_name, 0, info.shape, info.dtype)
            self.shm_ftsensor.execute(info)

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
    
    def streaming_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_streaming = True
        self.logger.info('Start streaming ...')
        while self.is_streaming:
            self.shm_ftsensor.execute(np.array(self.get_info()).astype(np.int64))
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
        
    def _close_shm(self):
        '''
        Close shared memory objects.
        '''
        if self.with_streaming:
            self.shm_ftsensor.close()
    
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
